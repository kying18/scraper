import urllib.request
from lxml import html
import pymysql
import smtplib

from email.message import EmailMessage

import config
from library.database import query, prevent_sql_injection, close_connection

class FacebookScraper(object):
    """
    Object to scrape posts from a Facebook page.
    """
    def __init__(self, page_ids, connection):
        """
        Initializes Facebook Scraper object
        :param page_ids: strings of page IDs to scrape from as an iterable
            These are the end of the URL that links to the Facebook page, ie:
                www.facebook.com/scraper/ --> page ID is 'scraper'
        :param connection: pymysql connection object
        """
        self.page_ids = page_ids
        self.connection = connection

    def _get_profile_html(self, page_id):
        """
        Gets the html of the profile
        :param page_id: page ID as a string
        :return: filelike object representing html on specified page
        """
        profile = urllib.request.urlopen(config.FB_LINK.format(page_id)).read()
        with open('profile.html', 'wb') as f:
            f.write(profile)
        return profile

    def _scrape_profile(self, page_id):
        """
        Gets the new posts from a Facebook profile
        :param page_id: string, page ID of profile
        :return: list of new posts
        """
        new_posts = []

        # gets profile from Facebook page
        profile = self._get_profile_html(page_id)
        page = html.fromstring(profile)

        # gets the div of a post
        divs = page.xpath(".//div[contains(@class,'userContent')]")
        for div in divs:
            lines = div.xpath(".//p")
            text = ''
            # gets text of multi-line posts
            for line in lines:
                text += line.xpath("string(.)") + '\n'

            new_posts.append(text)

        return new_posts

    def get_new_posts(self):
        """
        Gets the new posts from the pages if not in the database
        :return: None
        """
        new_posts = []

        # for each profile
        for page_id in self.page_ids:
            # get new posts
            for post in self._scrape_profile(page_id):
                if len(new_posts) == 0 or post != new_posts[-1]:
                    post = prevent_sql_injection(post)
                    sql = "CALL sys.InsertPost('{post}', '{page}');".format(post=post, page=page_id)
                    query(self.connection, sql, results=False)

    def email_posts(self):
        """
        Email posts to specified recipients
        :return: None
        """
        sql = 'SELECT id, post_text FROM sys.FacebookPosts WHERE notified=0;'
        db_results = query(self.connection, sql, commit=False)
        posts = [result['post_text'] for result in db_results]

        if not posts:
            return

        msg = EmailMessage()
        content = ''
        for post in posts:
            content += (post + '\n\n\n')
        msg.set_content(content)
        #
        # # me == the sender's email address
        # # you == the recipient's email address
        msg['Subject'] = 'Confessions Update'
        msg['From'] = config.EMAIL
        msg['To'] = config.RECIPIENTS

        # Send the message via our own SMTP server.
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(config.EMAIL, config.PWORD)
        s.send_message(msg)
        s.quit()

        notified_ids = [str(result['id']) for result in db_results]
        sql = 'UPDATE sys.FacebookPosts SET notified=1 ' \
              'WHERE id IN ({ids});'.format(ids=','.join(notified_ids))
        query(self.connection, sql, commit=True)

    def scrape(self):
        """
        Scrapes and emails posts
        :return: None
        """
        self.get_new_posts()
        self.email_posts()
        close_connection(self.connection)

if __name__ == '__main__':
    connection = pymysql.connect(host='localhost',
                           user=config.DB_USER,
                           password=config.DB_PASS,
                           db='sys',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    scraper = FacebookScraper([config.TIMELY_CONFESSIONS, config.CONFESSIONS], connection)
    scraper.scrape()

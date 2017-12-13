import urllib.request
from lxml import html
import pickle
import smtplib

from email.message import EmailMessage

import config

class FacebookScraper(object):
    """
    Object to scrape posts from a Facebook page.
    """
    def __init__(self, page_ids):
        """
        Initializes Facebook Scraper object
        :param page_ids: strings of page IDs to scrape from as an iterable
            These are the end of the URL that links to the Facebook page, ie:
                www.facebook.com/scraper/ --> page ID is 'scraper'
        """
        self.page_ids = page_ids

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

    def _get_previous_posts(self, pickle_file):
        """
        Gets the previous posts existing
        :param pickle_file: path to pickle file consisting of previously scraped posts
        :return: previously saved posts
        """
        with open(pickle_file, 'rb') as p:
            posts = pickle.load(p)
        return posts

    def _save_posts(self, pickle_file, posts):
        """
        Saves posts to pickle file
        :param pickle_file: path to pickle file consisting of previously scraped posts
        :param posts: posts to save to pickle file
        :return: None
        """
        with open(pickle_file, 'wb') as p:
            pickle.dump(posts, p)

    def _scrape_profile(self, page_id, posts):
        """
        Gets the new posts from a Facebook profile
        :param page_id: string, page ID of profile
        :param posts: previous posts
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

            # if not already posts, add to set
            if (text, page_id) not in posts:
                new_posts.append((text, page_id))

        # save new posts
        self._save_posts(config.POSTS_PATH, (set(new_posts) | posts))

        return new_posts

    def get_new_posts(self):
        """
        Returns a list of new posts
        :return: list of new posts
        """
        new_posts = []

        # for each profile
        for page_id in self.page_ids:
            previous_posts = self._get_previous_posts(config.POSTS_PATH)

            # get new posts
            for post, _ in self._scrape_profile(page_id, previous_posts):
                if len(new_posts) == 0 or post != new_posts[-1]:
                    new_posts.append(post)
                    print(post)

        return new_posts

    def email_posts(self, posts):
        """
        Email posts to specified recipients
        :param posts: list of posts to email
        :return: None
        """
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
        # s.send_message(msg)
        s.quit()

    def scrape(self):
        """
        Scrapes and emails posts
        :return: None
        """
        new_posts = self.get_new_posts()
        self.email_posts(new_posts)


if __name__ == '__main__':
    if config.RESET_SAVED_POSTS:
        with open(config.POSTS_PATH, 'wb') as p:
            pickle.dump(set(), p)
    scraper = FacebookScraper([config.TIMELY_CONFESSIONS, config.CONFESSIONS])
    scraper.scrape()

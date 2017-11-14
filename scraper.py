import urllib.request
from lxml import html
import pickle
import smtplib

from email.message import EmailMessage

import config

class FacebookScraper(object):
    def __init__(self, page_ids):
        self.page_ids = page_ids

    def _get_profile_html(self, page_id):
        profile = urllib.request.urlopen(config.FB_LINK.format(page_id)).read()
        with open('profile.html', 'wb') as f:
            f.write(profile)
        return profile

    def _get_previous_posts(self, pickle_file):
        with open(pickle_file, 'rb') as p:
            posts = pickle.load(p)
        return posts

    def _save_posts(self, pickle_file, posts):
        with open(pickle_file, 'wb') as p:
            pickle.dump(posts, p)

    def _scrape_profile(self, page_id, posts):
        new_posts = []

        profile = self._get_profile_html(page_id)
        page = html.fromstring(profile)
        divs = page.xpath(".//div[contains(@class,'userContent')]")
        for div in divs:
            lines = div.xpath(".//p")
            for line in lines:
                text = line.xpath("string(.)")
                if (text, page_id) not in posts:
                    new_posts.append((text, page_id))

        self._save_posts(config.POSTS_PATH, (set(new_posts) | posts))

        return new_posts

    def get_new_posts(self):
        new_posts = []
        for page_id in self.page_ids:
            previous_posts = self._get_previous_posts(config.POSTS_PATH)
            for post, _ in self._scrape_profile(page_id, previous_posts):
                if len(new_posts) == 0 or post != new_posts[-1]:
                    new_posts.append(post)
                    print(post)

        return new_posts

    def email_posts(self, posts):
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
        new_posts = self.get_new_posts()
        self.email_posts(new_posts)


if __name__ == '__main__':
    if config.RESET_SAVED_POSTS:
        with open(config.POSTS_PATH, 'wb') as p:
            pickle.dump(set(), p)
    scraper = FacebookScraper([config.TIMELY_CONFESSIONS, config.CONFESSIONS])
    scraper.scrape()

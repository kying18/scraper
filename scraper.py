import urllib.request
from lxml import html

import config

def get_profile_html():
    profile = urllib.request.urlopen(config.FB_LINK.format(config.USER)).read()
    with open('profile.html', 'wb') as f:
        f.write(profile)

    return profile


def scrape_profile(profile):
    page = html.fromstring(profile)

    divs = page.xpath(".//div[contains(@class,'userContent')]")
    for div in divs:
        lines = div.xpath(".//p")
        for line in lines:
            text = line.xpath("string(.)")
            print(text)




if __name__ == '__main__':
    # urllib.request.urlopen('https://graph.facebook.com')
    profile = get_profile_html()
    scrape_profile(profile)
    # div = 'recent_capsule_container'
    # local_filename, headers = urllib.request.urlretrieve(config.FB_LINK.format(config.USER))
    # html = open(local_filename)

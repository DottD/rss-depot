from os import truncate
import re
import json
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime, timezone, timedelta
from inspect import cleandoc
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup

base_name = 'bce-vacancies'
with Path(f'{base_name}.json').open('r') as f:
    conf = json.loads(f.read())
url = conf['url']

# Scraping
r = requests.get(url, allow_redirects=True)
text_strip = lambda x: x.text.strip()
# Initialize the parser
soup = BeautifulSoup(r.text, 'html.parser')
# Create the feed
fg = FeedGenerator()
fg.id(url)
fg.title('BCE Vacancies')
fg.description(text_strip(soup.find("title")))
fg.author({'name': conf['author_name'], 'email': conf['author_email']})
fg.link(href=url, rel='alternate')
fg.logo(urljoin(url, soup.find("link", attrs={'id': 'favico'}).attrs['href'])) # also sets rss:image
fg.language('en')
tz = timezone(offset=timedelta(hours=1))
pubDate = datetime.now(tz)
fg.updated(pubDate)
# Analysis
search_recap = text_strip(soup.select_one("div.list-controls__legend"))
non_paginated_results = int(re.search("(\d+)", search_recap)[0]) # may throw
    
while non_paginated_results > 0:
    for row in soup.select("div.article__header__text"):
        # Fetches item's information
        title_html_element = row.select_one('.article__header__text__title a')
        title = text_strip(title_html_element)
        link = title_html_element.attrs['href'].strip()
        comp_loc_raw = row.select_one('.article__header__text__subtitle')
        field = comp_loc_raw.select_one('.icon-interest + span:not([class])')
        if field:
            field = text_strip(field)
        else: field = ''
        level = comp_loc_raw.select_one('.icon-level + span:not([class])')
        if level:
            level = text_strip(level)
        else: level = ''
        area = comp_loc_raw.select_one('.icon-businessArea + span:not([class])')
        if area:
            area = text_strip(area)
        else: area = ''
        deadline = comp_loc_raw.select_one('.icon-calendar + span:not([class])')
        if deadline:
            deadline = text_strip(deadline)
        else: deadline = ''
        # Look for info in the item link
        inner_r = requests.get(link, allow_redirects=True)
        inner_soup = BeautifulSoup(inner_r.text, 'html.parser')
        descr = text_strip(inner_soup.select_one('div.article__content'))
        # Builds the item
        fe = fg.add_entry(order='append')
        fe.title(title)
        fe.link(href=link, rel='alternate')
        fe.guid(guid=link, permalink=True)
        fe.description(f"{field} - Deadline: {deadline}")
        fe.content(cleandoc(f"""
        <div>
            <h2>{title}</h2>
            <p><b>Field: </b><i>{field}</i></p>
            <p><b>Level: </b><i>{level}</i></p>
            <p><b>Business Area: </b><i>{area}</i></p>
            <p><b>Dealine: </b><i>{deadline}</i></p>
            <br><hr><br>
            <h4>Description</h4>
            {descr}
        </div>
        """.replace('&amp;', '&')), type='CDATA')
        fe.pubDate(pubDate)
        # Decrement results count
        non_paginated_results -= 1
    if non_paginated_results > 0:
        # Explore next page
        next_link = soup.select_one("a.paginationNextLink")
        if next_link is not None:
            next_link = next_link.attrs['href'].strip()
            r = requests.get(next_link, allow_redirects=True)
            soup = BeautifulSoup(r.text, 'html.parser')
        else:
            break
rss_path = Path(f'rss-gen/{base_name}-rss.xml')
rss_path.parent.mkdir(exist_ok=True)
rss_content = fg.rss_str(pretty=False)
with rss_path.open('wb') as f:
    f.write(rss_content)
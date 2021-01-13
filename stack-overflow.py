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

with Path('stack-overflow.json').open('r') as f:
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
fg.title('Stack Overflow')
fg.description(text_strip(soup.find("title")))
fg.author({'name': conf['author_name'], 'email': conf['author_email']})
fg.link(href=url, rel='alternate')
fg.logo(soup.find("link", attrs={'rel': 'apple-touch-icon'}).attrs['href']) # also sets rss:image
fg.language('it')
tz = timezone(offset=timedelta(hours=1))
pubDate = datetime.now(tz)
fg.updated(pubDate)
# Analysis
search_recap = text_strip(soup.select_one("span.description"))
non_paginated_results = int(re.search("(\d+)", search_recap)[0]) # may throw
    
while non_paginated_results > 0:
    for row in soup.select("div.js-result div.grid--cell.fl1"):
        # Fetches item's information
        title_html_element = row.select_one('h2 a')
        title = text_strip(title_html_element)
        link = urljoin(url, title_html_element.attrs['href'].strip())
        comp_loc_raw = row.select("h3 span")
        via_span = list(filter(lambda x: x.text == 'via', comp_loc_raw))
        if via_span:
            via_span = via_span[0]
            comp_loc_raw.remove(via_span)
            company, location = tuple(map(text_strip, comp_loc_raw))
            company = re.sub(r'\s{2,}via\s{2,}', ' -> ', company)
        else:
            company, location = tuple(map(text_strip, comp_loc_raw))
        techs = ', '.join(tuple(map(text_strip, row.select("div > a"))))
        listed_features = row.select("ul li")
        published = text_strip(listed_features[0].select_one("span"))
        listed_features = ', '.join(tuple(map(text_strip, listed_features[1:])))
        # Look for info in the item link
        inner_r = requests.get(link, allow_redirects=True)
        inner_soup = BeautifulSoup(inner_r.text, 'html.parser')
        descr_json = ''.join(inner_soup.find("script", {"type": "application/ld+json"}).contents)
        descr = json.loads(descr_json).get('description', 'No available description')
        # Builds the item
        fe = fg.add_entry(order='append')
        fe.title(title)
        fe.link(href=link, rel='alternate')
        fe.guid(guid=link, permalink=True)
        fe.description(f"{listed_features} - {techs}")
        fe.content(cleandoc(f"""
        <div>
            <h2>{title}</h2>
            <p><b>Company: </b><i>{company}</i></p>
            <p><b>Location: </b><i>{location}</i></p>
            <p><b>Technologies: </b><i>{techs}</i></p>
            <p><b>Publication Date: </b><i>{published}</i></p>
            <p><b>Other features: </b><i>{listed_features}</i></p>
            <br><hr><br>
            <h4>Description</h4>
            {descr}
        </div>
        """), type='CDATA')
        fe.pubDate(pubDate)
        # Decrement results count
        non_paginated_results -= 1
    if non_paginated_results > 0:
        # Explore next page
        next_link = [
            urljoin(url, pag_item.attrs['href'].strip())
            for pag_item in soup.select("a.s-pagination--item")
            if pag_item.find("span").text == "next"
        ][0]
        r = requests.get(next_link, allow_redirects=True)
        soup = BeautifulSoup(r.text, 'html.parser')
rss_path = Path('rss-gen/stack-overflow-rss.xml')
rss_path.parent.mkdir(exist_ok=True)
rss_content = fg.rss_str(pretty=False)
with rss_path.open('wb') as f:
    f.write(rss_content)
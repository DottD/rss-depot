from os import truncate
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from inspect import cleandoc
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup

with Path('epso.json').open('r') as f:
    conf = json.loads(f.read())
url = conf['url']

# Scraping
r = requests.get(url, allow_redirects=True)
# Write web content to file for later inspection
# html_uri = Path('web_content.html')
# with html_uri.open('w') as f:
#     f.write(r.text)
# Initialize the parser
soup = BeautifulSoup(r.text, 'html.parser')
# Create the feed
fg = FeedGenerator()
fg.id(url)
fg.title('EPSO - Concorsi')
fg.description(soup.find("meta", attrs={'name': 'description'}).attrs['content'])
fg.author({'name': conf['author_name'], 'email': conf['author_email']})
fg.link(href=url, rel='alternate')
fg.logo('https://epso.europa.eu/sites/epso/themes/euc/favicon.ico') # also sets rss:image
fg.language('it')
tz = timezone(offset=timedelta(hours=1))
pubDate = datetime.now(tz)
fg.updated(pubDate)
# Analysis
for row in soup.select("tbody tr"):
    # Fetches item's information
    title = row.select_one('td.views-field-title-field')
    title_a = title.find("a")
    if title_a is None:
        continue
    func = title_a.text.strip()
    link = "https://epso.europa.eu/"+title_a.attrs['href'].strip()
    grade = row.select_one("td.views-field-field-epso-grade").text.strip()
    location = row.select_one("td.views-field-field-epso-locations").text.strip()
    agency = row.select_one("td.views-field-field-epso-institutions-agencies").text.strip()
    # Builds the item
    fe = fg.add_entry(order='append')
    fe.title(func)
    fe.link(href=link, rel='alternate')
    fe.guid(guid=link, permalink=True)
    fe.content(cleandoc(f"""
    <div>
        <div style="background-color: blue;">
            <img src="{soup.select_one("header img.c-banner").attrs['src']}" alt="EPSO Logo" style="max-width: 100%; height: auto; display: block; margin-left: auto; margin-right: auto;"/>
        </div>
        <p style="font-style: italic;">
            <b style="text-decoration: underline; font-style: normal;">
                Grado
            </b>: {grade}
        </p>
        <p style="font-style: italic;">
            <b style="text-decoration: underline; font-style: normal;">
                Sede/i
            </b>: {location}
        </p>
        <p style="font-style: italic;">
            <b style="text-decoration: underline; font-style: normal;">
                Istituzione/agenzia
            </b>: {agency}
        </p>
        <p style="font-style: italic;">
            <b style="text-decoration: underline; font-style: normal;">
                Tipo di contratto
            </b>: {row.select_one("td.views-field-field-epso-type-of-contract").text}
        </p>
        <p style="font-style: italic;">
            <b style="text-decoration: underline; font-style: normal;">
                Termine
            </b>: {row.select_one("td.views-field-field-epso-deadline span").text}
        </p>
    </div>
    """), type='CDATA')
    fe.pubDate(pubDate)
rss_path = Path('rss-gen/epso-rss.xml')
rss_path.parent.mkdir(exist_ok=True)
rss_content = fg.rss_str(pretty=False)
with rss_path.open('wb') as f:
    f.write(rss_content)
import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

class unilever (rss):
    """Scrapes Unilever"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "unilever (corp)"
        self.rss_url ='https://www.unilever.com/feeds/news.rss'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/article[@class="content-article"]/h1/text()')).strip()
        except:
            logger.warning("Could not parse article title")
            title = ""
        try:
            category="".join(tree.xpath('//*[@class="small-12 end"]/ul/li/a/text()')).strip()
        except:
            category = ""
            logger.debug("Could not parse article title")
        if len(category.split(" ")) >1:
            category=""
        try:
            teaser="".join(tree.xpath('//*[@class="intro"]/p/text()')).strip()
        except:
            logger.debug("Could not parse article title")
            teaser= ""
        teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*/article[@class="content-article"]/section//text()')).strip()
        except:
            logger.warning("Could not parse article text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

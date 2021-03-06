import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging
import requests

logger = logging.getLogger(__name__)

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

class thetelegraph(rss):
    """Scrapes telegraph.co.uk"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "telegraph (www)"
        self.rss_url = "http://www.telegraph.co.uk/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=9, day=11)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #logger.warning(doc)
            return("","","", "")
        try:
            title = "".join(tree.xpath("//*[@class='headline__heading']/text()"))
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            category = tree.xpath("//*[@class='breadcrumbs__item-content']/text()")[1]
        except:
            category = ""
            logger.debug("Could not parse article category")
        try:
            byline = "".join(tree.xpath("//*[@class='byline__author-name']//text()"))
        except:
            byline = ""
            logger.debug("Could not parse article source")
        try:
            text = "".join(tree.xpath("//*[@itemprop='articleBody']//p/text()|//*[@itemprop='articleBody']//a/text()|//*[@class='m_first-letter m_first-letter--flagged']//text()"))
        except:
            byline = ""
            logger.debug("Could not parse article source")

        extractedinfo={"title":title.strip().replace("\n",""),
                       "category":category.strip(),
                       "byline":byline.strip().replace("\n","").replace(",",""),
                       "text":text.strip().replace("\xa0","").replace("\\","")
                      }

        return extractedinfo

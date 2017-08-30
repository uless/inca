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

class diewelt(rss):
    """Scrapes welt.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "ad (www)"
        self.rss_url=['https://www.welt.de/feeds/latest.rss','https://www.welt.de/feeds/topnews.rss','https://www.welt.de/feeds/section/mediathek.rss','https://www.welt.de/feeds/section/video.rss','https://www.welt.de/feeds/section/politik.rss','https://www.welt.de/feeds/section/wirtschaft.rss','https://www.welt.de/feeds/section/wirtschaft/bilanz.rss','https://www.welt.de/feeds/section/finanzen.rss','https://www.welt.de/feeds/section/wirtschaft/webwelt.rss','https://www.welt.de/feeds/section/wissen.rss','https://www.welt.de/feeds/section/kultur.rss','https://www.welt.de/feeds/section/sport.rss','https://www.welt.de/feeds/section/icon.rss','https://www.welt.de/feeds/section/gesundheit.rss','https://www.welt.de/feeds/section/vermischtes.rss','https://www.welt.de/feeds/section/motor.rss','https://www.welt.de/feeds/section/reise.rss','https://www.welt.de/feeds/section/regional.rss','https://www.welt.de/feeds/section/debatte.rss']
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")

#category
        try:
            category = r[1]['url'].split('/')[3]
        except:
            category =""

#teaser
        try:
            teaser = tree.xpath('//*[@class="c-summary__intro"]//text()')
        except:
            teaser =""
#title
        try:
            title = tree.xpath('//*[@class="c-dreifaltigkeit__headline-wrapper"]//text()')[1] + " : " + tree.xpath('//*[@class="c-dreifaltigkeit__headline-wrapper"]//text()')[3]
        except:
            title =""
#text
        try:
            text = "".join(tree.xpath('//*[@class="c-dreifaltigkeit__headline-wrapper"]//text()'))
        except:
            text =""
       
#author
        try:
            author = tree.xpath('//*[@class="c-author__name"]//text()')[1]
        except:
            author =""
#source
        try:
            source = tree.xpath('//*[@class="c-source"]//text()')
        except:
            source =""
            
        extractedinfo={"category":category,
                       "title":title,
                       "text":text,
                       "teaser":teaser,
                       "byline":author,
                       "byline_source":source
                       }
        
        return extractedinfo

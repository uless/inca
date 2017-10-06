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

class ing(rss):
    """Scrapes ing - Nederland """

    def __init__(self,database=True):
        self.database=database
        self.doctype = "nu"
        self.rss_url='https://www.ing.nl/nieuws/nieuws_en_persberichten/news.xml?format=rss'
        self.version = ".1"
        self.date    = datetime.datetime(year=2018, month=10, day=6)

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
            teaser=tree.xpath('//*[@class="intro-text"]//text()')[0]
        except:
            logger.info("OOps - geen eerste alinea?")
            teaser=""
        try:
             text ="".join(tree.xpath('//*[@class="paragraph clearfix"]//text()')).strip()
        except:
             logger.info("Geen text?")
        text=polish(text)
        try:
            title ="".join(tree.xpath('//*[@class="intro"]//h1/text()')).strip()
        except:
            title = ""
            logger.warning("No title encountered")

        images = ing._extract_images(self,tree)

        releases={"teaser":teaser.strip(),
        "text":polish(text).strip(),
        "title":title,
        "images":images}
        return releases

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="paragraph clearfix"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src'],
                     'height' : img.attrib['height'],
                     'width' : img.attrib['width']}
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     #'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images


class walmart(rss):
    """Scrapes Walmart """

    def __init__(self,database=True):
        self.database = database
        self.doctype = "walmart (corp)"
        self.rss_url ='http://corporate.walmart.com/rss?feedName=allnews'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=1, day=1)


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
            title="".join(tree.xpath('//*[@class="article-header-title"]/text()')).strip()
        except:
            print("no title")
            title = ""
        try:
            category="".join(tree.xpath('//*[@class="article-header-tags"]//a/text()')).strip()
            print("this prints category", category)
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            text="".join(tree.xpath('//*[@class="article-content"]/p/text()')).strip()
        except:
            print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        releases={"title":title.strip(),
                  "category":category.strip(),
                  "text":polish(text).strip()
                  }

        return releases
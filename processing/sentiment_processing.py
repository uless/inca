# -*- coding: utf-8 -*-
from core.processor_class import Processer
from core.basic_utils import dotkeys
import logging
import re
import sys
from nltk.sentiment import vader


logger = logging.getLogger(__name__)



class sentiment_vader_en(Processer):
    '''Sentiment-analyses English-language texts using Vader'''

    def process(self, document_field):
        '''Document was split into paragraphs'''
        try:
            senti=vader.SentimentIntensityAnalyzer()
            sentimentscores = senti.polarity_scores(document_field)
            return sentimentscores
        except LookupError:
            from nltk import download
            download('vader_lexicon')
            logger.error("Couldn't find Vader Lexicon, downloaded it\nYou will have to re-run the processor")           

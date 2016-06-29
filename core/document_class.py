'''
This document class is the template for classes that add or update
documents in the database. The scraper and update classes inherit
from this class. 

The basic functionality is adding meta-data 

'''

import logging
import datetime
from celery import Task

logger = logging.getLogger(__name__)

from core.database import insert_document, update_document

class Document(Task):
    '''
    Documents reflect the basic format of documents in the datastore. 
    On save attempts, this class tries to infer whether required fields 
    are present. 

    The 'META' key contains a key:description of all other keys in the document. 
    
    '''

    

    functiontype = ''
    version      = ''
    date         = ''
    

    def _save_document(self, document, forced=False):
        '''
        Documents are saved to the general document collection
        defined in the core.database file.

        Update existing documents by passing an elasticsearch results 
        through the _update_document method. 

        Note that by default, documents can only extend, not replace
        old documents. 

        '''
        document['doctype'] = ''.join(__name__.split('_')[:-1])
        if '_id' in document.keys():
            custom_identifier = document.pop('_id')
        else :
            custom_identifier = None
        insert_document(document, custom_identifier=custom_identifier)

    def _update_document(self, new_document_body):
        '''
        This method updates exiting documents. It should map an elasticsearch
        result to a new body (the old body is in elasticsearch_result['_source']).
        '''
        update_document(new_document_body)

    def _add_metadata(self,document, **kwargs):
        '''
        DO NOT OVERWRITE THIS METHOD

        This method generates the metadata for returned documents based on 
        the 'get' function docstring and arguments.

        All new keys are reflected in the 'META' key with the information 
        about the script in question. 

        '''
        meta = dict(
            ADDED_AT              = datetime.datetime.now(),
            ADDED_USING           =str(self.__class__).split(' ')[1],
            ADDED_METHOD          = self.get.__doc__,
            FUNCTION_VERSION      = self.version,
            FUNCTION_VERSION_DATE = self.date,
            FUNCTION_TYPE         = self.functiontype,
            FUNCTION_ARGUMENTS    = kwargs
            )

        if not document.get('META',False):
            document['META']=dict()

        for key in document.keys():
            if key == 'META': continue
            if key not in document['META'].keys():
                document['META'][key] = meta

        return document
    
    def _verify(self, document):
        '''
        DO NOT OVERWRITE THIS METHOD

        This method verifies whether yielded documents conform to the specification 
        of the datastore
        '''
        
        assert type(document)==dict
        assert document.get('META',False), "document lacks a `meta` key"
        for key in document.keys():
            if key=='META': continue
            assert key in document['META'], "meta key for %s is missing from documents!" %key

    def _check_complete(self):
        '''
        DO NOT OVERWRITE THIS METHOD

        This method checks whether the appropriate information is present in the subclass. 
        '''

        for attribute in ['functiontype','version','date','doctype']:
            if not getattr(self,attribute):
                logger.warning("""%s misses the appropriate `%s` property! 
                Please set these in the class __init__ method as self.%s""" %(
                    self.__class__, attribute,attribute))

        teststrings = [''' This docstring should explain how documents are transformed ''',
                       ''' This docstring should explain how documents are retrieved ''' ]

        for method in ['process','get']:
            try:
                if getattr(self,method).__doc__ in teststrings:
                    logger.warning("""%s's %s docstring does not reflect functionality! 
                    Please update the docstring in your class definition.""" %(self.__class__, method))
            except:
                pass

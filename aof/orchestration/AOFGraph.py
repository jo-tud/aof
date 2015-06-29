from rdflib import Dataset, Namespace
from rdflib.plugins.memory import IOMemory
from aof.orchestration.namespaces import AOF
from rdflib import ConjunctiveGraph
from urllib.parse import urlparse
from hashlib import md5
import pyqrcode
import os
import logging
from pyramid.path import AssetResolver

__author__ = 'khoerfurter'
log = logging.getLogger(__name__)

__all__ = [
    'AOFGraph'
]

'''
This class extends Dataset which in turn extends ConjunctiveGraph, initializes a store and makes it a Singleton
'''

class AOFGraph(ConjunctiveGraph):

    def __init__(self,identifier):
        pass
        store = IOMemory() # TODO: Change the storage mechanism to a persistent one and implement caching
        #d=Dataset(self, store=store,default_union=True)

        ConjunctiveGraph.__init__(self, store=store, identifier=identifier)

        # Make sure the aof namespace is always known to AOFGraph
        self.bind('aof', AOF)


    def _hash_value(self,value):
        """
        Makes an md5-Hash of an value
        :param value: string (value to hash)
        :return: string
        """
        hash=md5()
        hash.update(value.encode('utf-8'))
        return str(hash.hexdigest())


    def get_QRCode(self,url,size=4):
        """
        Generates an QR-Code-SVG into the directory "static/img/qrcodes"
        Filename of the SVG is an md5-hash of the uri.
        :return: relative URL or None if the url is not valid
        """

        valid_url=urlparse(url)
        if bool(valid_url.scheme):
            hash=self._hash_value(url)
            target=AssetResolver().resolve(os.path.join('aof:tmp','qrcodes',hash+".svg")).abspath()
            if not os.path.exists(target):
                qrcode = pyqrcode.create(url)
                qrcode.svg(target,size)
            target=target.replace(AssetResolver().resolve('aof:').abspath(),"")
            target=target.replace('\\',"/")
            qrcode=target
        else:
            log.error("QRCode for {} could not be created. Seems to be an invalid URL!".format(url))
            qrcode = None
        return qrcode

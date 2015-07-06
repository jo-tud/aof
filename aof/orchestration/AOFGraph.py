from rdflib import Dataset, Namespace
from rdflib import  util
from rdflib.plugins.memory import IOMemory
from aof.orchestration.namespaces import AOF, ANDROID
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, RDFS
from rdflib import ConjunctiveGraph
from rdflib import  URIRef
from urllib.parse import urlparse
from rdflib.exceptions import UniquenessError
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

    init_format="turtle"

    def __init__(self,identifier):
        pass
        store = IOMemory() # TODO: Change the storage mechanism to a persistent one and implement caching
        #d=Dataset(self, store=store,default_union=True)

        ConjunctiveGraph.__init__(self, store=store, identifier=identifier)

        # Make sure the aof namespace is always known to AOFGraph
        self.bind('aof', AOF)


    def in_pool(self, resource):
        """
        Searches for an specific AppEnsemble.
        :param resource: String (Name of the App
        :return:Boolean
        """
        q = ("ASK WHERE {<%(uri)s> ?p ?o .}")% {'uri': URIRef(resource)}
        return self.query(q).askAnswer

    def load(self, source, format=None):
        """
        Loads  the source into the Graph
        :param source:
        :param format:
        :return:
        """
        if format==None:
            format=self.init_format

        super().load(source, format=format)

    def is_resource_of_type(self,resource,type,use_sparql=False):
        if use_sparql:
            q = ("ASK WHERE {<%(uri)s> a <%(type)s> .}") % {'uri': resource, 'type': type}
            return self.query(q).askAnswer
        else:
            return ((resource, URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), type) in self)

    # TODO: Check type of subject,predicate
    def has_tuple(self,subject,predicate,use_sparql=False):
        """
        Searches the Graph for subject-predicate tuples
        :param resource: URI-Ref
        :param property: URI-REf
        :param use_sparql: Boolean
        :return: Boolean
        """
        if use_sparql:
            q = ("ASK WHERE {<%(uri)s> <%(predicate)s> ?role .}") % {'uri': subject, 'predicate': predicate}
            return self.query(q).askAnswer
        else:
            return ((subject, predicate, None) in self)

    # TODO: Check type of subject,predicate
    # TODO: Implemente sparql-method to do the same link in has_tuple
    def get_tuples(self,subject,predicate,to_string=False):
        """
        Returns all tuples which match (subject, predicate, none)
        :param subject: 
        :param predicate: 
        :param to_string: 
        :return: list
        """
        results = self.objects(subject, predicate)
        result_list = list()
        for result in results:
            if to_string:
                result=result.__str__()
            result_list.append(result)
        return result_list

    # TODO: Check type of subject,predicate
    def get_tuple(self,subject,predicate,to_string=False):
        """
        Returns one tuple which match (subject, predicate, none)
        :param subject: 
        :param predicate: 
        :param to_string: 
        :return:
        """

        try:
            result=self.value(subject, predicate,any=False)
            if to_string:
                result=result.__str__()
        except UniquenessError:
            result=self.get_tuples(subject,predicate,to_string)

        return result

    def get_tuple_list(self, subject, predicate_list, predicate_cardinality_greater_one=[], to_string=False):
        """
        Returns one tuple for each element of the predicate_list which matches(subject, predicate_list_item, none)
        :param subject:
        :param predicate_list:
        :param predicate_cardinality_greater_one: keys out of the predicate_list where the objects should be returnd as a list
        :param to_string:
        :return:
        """
        results = dict()
        if type(subject)==URIRef:
            results['uri']=subject.__str__()
        for predicate_key, predicate_value in predicate_list.items():
            if predicate_key in predicate_cardinality_greater_one:
                results[predicate_key]=self.get_tuples(subject, predicate_value,to_string)
            else:
                results[predicate_key]=self.get_tuple(subject, predicate_value,to_string)
        return results
    
    def get_tuples_with_subtuples_list(self, subject,predicate, sub_predicate_dict, predicate_cardinality_greater_one=[], to_string=False):
        """
        Returns one tuple which matches (subject, predicate, object) and one tuple for each element of the sub_predicate_dict which matches (object, predicate_list_item, none)
        :rtype : object
        :param subject: 
        :param predicate: 
        :param sub_predicate_list:
        :param to_string: 
        :return:
        """
        results = list()
        for result in self.get_tuples(subject, predicate):
            results.append(self.get_tuple_list(result, sub_predicate_dict,predicate_cardinality_greater_one, to_string=to_string))
            
        return results

    #TODO move into helper class
    def _hash_value(self,value):
        """
        Makes an md5-Hash of an value
        :param value: string (value to hash)
        :return: string
        """
        hash=md5()
        hash.update(value.encode('utf-8'))
        return str(hash.hexdigest())

    #TODO move into helper class
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

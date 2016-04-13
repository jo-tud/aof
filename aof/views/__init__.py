import logging
from rdflib import RDF, RDFS
from rdflib.namespace import DC, FOAF
from aof.orchestration.namespaces import AOF, ANDROID
from urllib.parse import urljoin

__all__ = ["AppEnsembleViews", "AppPoolViews", "DocumentationViews","Views"]

__author__ = 'khoerfurter'
namespaces = {'AOF': AOF, 'ANDROID': ANDROID, 'DC': DC, 'FOAF': FOAF, 'RDF': RDF, 'RDFS': RDFS}
log = logging.getLogger(__name__)


class AbstractViews():
    def __init__(self, context, request):
        """
        Super-Class of all AOF-Views.
        Provides the context and request-paramter
        """
        self.context = context
        self.request = request


    def _returnCustomDict(self, *args):
        """
        Matches all argument for an dictionary-return
        :param args: dictionary of return arguments
        :return: dictionary
        """
        return_args = dict()
        for arg in args:
            if arg is not None:
                return_args.update(arg)
        return return_args

    #TODO: write Test
    def get_URI(self,route):

        if route == None:
            log.error('No route is provided for URI-generation')
            return None
        else:
            introspector = self.request.registry.introspector
            uri = introspector.get('routes', route)
            if uri != None:
                uri=str(uri['pattern'])
                uri= urljoin(self.request.application_url,uri)
                return uri
            else:
                log.info("Routes are not available for URI-Generation")
                return ""

    def build_URI(self,route,replace_from, replace_with):
        uri=self.get_URI(route)
        uri=uri.replace(replace_from,replace_with)
        return uri
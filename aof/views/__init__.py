import logging
from rdflib import RDF, RDFS
from rdflib.namespace import DC, FOAF
from aof.orchestration.namespaces import AOF, ANDROID

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
from functools import wraps
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from rdflib import URIRef
from aof.orchestration.AOFGraph import AOFGraph
from aof.orchestration.AppEnsemblePool import AppEnsemblePool
from aof.orchestration.AppPool import AppPool
from aof.views import AbstractViews
from urllib.parse import unquote_plus

import os
import logging
import ast

__author__ = 'khoerfurter'
log = logging.getLogger(__name__)

class RequestPoolURI_Decorator(object):
    """
    Decorator Function:
    - Was an URI supplied
    - Was only one URI supplied
    - Was an URI supplied but the value empty
    - Does the supplied uri has an reference in the AppPool or AppEnsemblePool

    # Add this to Methods which use URIs to get Information about Elements out of the appPool or AppEnsemblePool
    """

    def __call__(self, f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):

            if not self.request.params.has_key('URI') and 'URI' not in self.request.matchdict:
                return Response(
                    'The parameter "URI" was not supplied. Please provide the URI of the App-Ensemble for which you want to display the details.')
            else:
                if len(self.request.params.getall('URI')) > 1  and 'URI' not in self.request.matchdict:
                    return Response('More than one URI was supplied. Please supply exactly 1 URI.')
                else:
                    if 'URI' in self.request.matchdict:
                        uri=self.request.matchdict['URI']
                    else:
                        uri = self.request.params.getone('URI')
                    if uri == "":
                        return Response(
                            'Value of the "URI"-parameter was empty. Please provide the URI of the resource.')
                    else:
                        self.uri = URIRef(unquote_plus(uri))
                        if isinstance(self.pool, AppPool):
                            if "://" not in self.uri and len(self.uri)==32:
                                for app in self.pool.get_app_uris():
                                    if str(self.uri) == self.pool._hash_value(app):
                                        self.uri=app
                                        break
                            if self.pool.in_pool(self.uri):
                                return f(self, *args, **kwargs)
                            else:
                                return HTTPNotFound('The uri "%s" could not be found in the AppPool.' % self.uri)
                        elif isinstance(self.pool, AppEnsemblePool):
                            if self.uri in self.pool:
                                self.uri = URIRef(self.uri)
                                return f(self, *args, **kwargs)
                            else:
                                return HTTPNotFound(
                                    'The uri "%s" could not be found in the AppEnsemblePool.' % self.uri)
                        else:
                            return log.error(
                                'URIExistDecorator was called without an AppPool or an AppEnsemblePool. The given object was an instance of {} and the pool was of type {}'.format(
                                    type(self), type(self.pool)))

                        return f(self, *args, **kwargs)

        return wrapper


class PageViews(AbstractViews):
    def __init__(self, context, request):
        """
        Super-Class for all Pages. Adds the pool and the page-title attribute
        """
        super(PageViews, self).__init__(context, request)
        self.pool = None
        self.page_title = None


        self.meta = ast.literal_eval(self.request.registry.settings['META'])

    def _returnCustomDict(self, *args):
        """
        Adds the return-dictionary-parameters for and HTML-Page
        :param args: dictionary of return arguments
        :return: dictionary
        """
        if self.page_title == None:
            import inspect

            log.error('HTML-Page has no title (Calling method:{})'.format(inspect.stack()[1][3]))
            self.page_title = "Not defined"
        custom_args = {'meta': self.meta, 'page_title': self.page_title}
        return super(PageViews, self)._returnCustomDict(custom_args, *args)

    def _setTitle(self, value):
        """
        Sets the page-title
        :param value: page-title [string]
        :return: NONE
        """
        self.page_title = str(value)
        return None


    @view_config(route_name='home', renderer='aof:templates/home.mako')
    def page_home(self):
        """
        Generates the parameters for the Home-page
        """
        self._setTitle('AOF Home')
        ap = AppPool.Instance()
        aem = AppEnsemblePool.Instance()
        number_of_apps = str(ap.get_number_of_apps())
        number_of_ae = str(len(aem))
        # TODO: are unique triples important
        #g = AOFGraph.Instance()
        #unique_triples = str(ap.__len__()+aep.__len()__)
        #unique_triples="1" HTML-code: <li>The model currently consists of ${unique_triples} unique triples!</li>

        ae_inst_uri=URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AppEnsembleInstaller/lastSuccessfulBuild/")
        ae_inst_arifact=ap.get_install_uri(ae_inst_uri)
        ae_inst_qrcode=ap.get_QRCode(ae_inst_arifact)


        custom_args = {'number_of_apps': number_of_apps,
                       'number_of_ae': number_of_ae,
                       #'unique_triples': unique_triples,
                       'ae_inst_uri' : self.build_URI('app-details','{URI:.*}',ap._hash_value(ae_inst_uri)),
                       'ae_inst_qrcode':ae_inst_qrcode,
                       'app_pool_uri':self.get_URI('apps'),
                       'app_ensemble_pool_uri':self.get_URI('app-ensembles')
                       }
        return self._returnCustomDict(custom_args)


if __name__ == "__main__":
    pass
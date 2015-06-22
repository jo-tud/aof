from functools import wraps
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from rdflib import URIRef
from aof.orchestration.AOFGraph import AOFGraph
from aof.orchestration.AppEnsemblePool import AppEnsemblePool
from aof.orchestration.AppPool import AppPool
from aof.views import AbstractViews

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
            if not self.request.params.has_key('URI'):
                return Response(
                    'The parameter "URI" was not supplied. Please provide the URI of the App-Ensemble for which you want to display the details.')
            else:
                if len(self.request.params.getall('URI')) > 1:
                    return Response('More than one URI was supplied. Please supply exactly 1 URI.')
                else:
                    uri = self.request.params.getone('URI')
                    if uri == "":
                        return Response(
                            'Value of the "URI"-parameter was empty. Please provide the URI of the App-Ensemble.')
                    else:
                        self.uri = URIRef(uri)
                        if isinstance(self.pool, AppPool):
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

    def _generateQRCode(self,url,size=4):
        """
        Generates an QR-Code-SVG into the directory "static/img/qrcodes"
        Filename of the SVG is an md5-hash of the uri.
        :return: relative URL or None if the url is not valid
        """
        import pyqrcode
        from pyramid.path import AssetResolver
        from urllib.parse import urlparse
        from hashlib import md5

        valid_url=urlparse(url)
        if bool(valid_url.scheme):
            hash=md5()
            hash.update(url.encode('utf-8'))
            target=AssetResolver().resolve(os.path.join('aof:tmp','qrcodes',str(hash.hexdigest())+".svg")).abspath()
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
        g = AOFGraph.Instance()
        unique_triples = str(g.__len__())

        ae_inst_uri=URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AppEnsembleInstaller/lastSuccessfulBuild/")
        ae_inst_arifact=ap.get_install_uri(ae_inst_uri)
        ae_inst_qrcode=self._generateQRCode(ae_inst_arifact)


        custom_args = {'number_of_apps': number_of_apps,
                       'number_of_ae': number_of_ae,
                       'unique_triples': unique_triples,
                       'ae_inst_uri' : ae_inst_uri,
                       'ae_inst_qrcode':ae_inst_qrcode
                       }
        return self._returnCustomDict(custom_args)


if __name__ == "__main__":
    print(PageViews(1,2)._generateQRCode("http://www.cyt.de/test.html?a=b&c=d",1))
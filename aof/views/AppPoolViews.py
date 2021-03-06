from functools import wraps
import logging

from pyramid.response import Response
from pyramid.view import view_config
from webhelpers2 import text

from rdflib import ConjunctiveGraph,Graph, BNode, URIRef

from aof.orchestration.AppPool import AppPool
from aof.orchestration.namespaces import AOF
from aof.views import namespaces
from aof.views.PageViews import PageViews, RequestPoolURI_Decorator
from urllib.parse import urljoin
from urllib.parse import quote_plus

__author__ = 'khoerfurter'
log = logging.getLogger(__name__)

# TODO: Check for speed optimization
def fill_graph_by_subject(basegraph, newgraph, subject, loop_count=0):
    """
    Fills an Graph with all triples with an certain subject. Includes the necessary triples for the objects until the deepth of 5.
    :param basegraph: Graph with the data for the new Graph
    :param newgraph: Instance of the new Graph
    :param subject: subject of triples which is looked for in the basegraph
    :return: Graph
    """
    subject_list=[BNode,URIRef]

    if not issubclass(type(basegraph),Graph):
        log.error("The given basegraph is not a subclass of Graph!")
        return ConjunctiveGraph()
    elif subject == "":
        log.info("The given subject was empty. Returning the basegraph")
        return basegraph
    elif type(subject) not in subject_list:
        log.info("The given subject was not of type BNode or URIRef. Returning the basegraph")
        return basegraph
    elif not issubclass(type(newgraph),Graph):
        newgraph=ConjunctiveGraph()

    loop_count += 1
    for s, p, o in basegraph.triples((subject, None, None)):
        newgraph.add((s, p, o))
        if type(o) in subject_list and loop_count < 6:  # it will do: (S1,P1,O1) -> if O1 has an own Description: (O1,P2,O2)... 5 times
            newgraph = fill_graph_by_subject(basegraph, newgraph, o, loop_count)
    return newgraph


class AppCheckDecorator(object):
    """
    Decorator function:
    - Is the URI of the object the URI of an Android-App

    # Use this only for Methods only with an AppPool as class-attibute pool
    """

    def __call__(self, f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if (hasattr(self, "pool") and isinstance(self.pool, AppPool)):
                if self.pool.is_android_app(self.uri) != True:
                    return Response(
                        "The app '%s' doesn't seem to be an Android App. Currently only Android Apps are supported." % self.uri)
                else:
                    return f(self, *args, **kwargs)
            else:
                import inspect

                log.info('AppCheckDecorator is used for a method ({}) without AppPool!'.format(inspect.stack()[1][3]))
                return f(self, *args, **kwargs)

        return wrapper


class AppPoolViews(PageViews):
    def __init__(self, context, request):
        """
        Class with all AppPool-Pages and -Actions
        """
        super(AppPoolViews, self).__init__(context, request)
        self.pool = AppPool.Instance()

    @view_config(route_name='apps', renderer='aof:templates/app-pool.mako')
    def page_overview(self):
        """
        Generates the parameters for the AppPool-Homepage
        """
        self._setTitle('App-Pool')

        apps = list()
        app_uris = self.pool.get_app_uris()
        for app_uri in app_uris:
            app = {
                'uri': app_uri,
                'details_uri':self.build_URI('app-details',"{URI:.*}",self.pool._hash_value(app_uri)),#/apps/"+quote_plus(app_uri)+"/details",
                'name': self.pool.get_name(app_uri),
                'icon': self.pool.get_icon_uri(app_uri),
                'binary': self.pool.get_install_uri(app_uri),
                'description': text.truncate(self.pool.get_description(app_uri), length=200, indicator='...', whole_word=True)
            }
            apps.append(app)

        apps = sorted(apps, key=lambda app: (app['name'], app['uri']))

        custom_args = {'apps': apps}
        return self._returnCustomDict(custom_args)

    @view_config(route_name='api-action-apps-update')
    def action_update(self):
        """
        Action: Update the AppPool from current AppPool definition
        :return: Response Object with number of Apps
        """
        self.pool.load(source=None, format='turtle')
        res = str(self.pool.get_number_of_apps())
        return Response(res,)

    @view_config(route_name='api-apps', renderer='json')
    def api_json(self):
        """
        Generates the pool in Json
        :return: json-representation of the AppPool
        """
        # log.debug("called view: ap_get_app_pool_json()")
        query = """
        PREFIX aof: <%(AOF)s>
        SELECT DISTINCT *
        WHERE {
        ?uri rdfs:label ?name ;
            aof:hasInstallableArtifact ?binary .
            OPTIONAL {
            ?uri aof:hasIcon ?icon
            }

        }
        ORDER BY ?name
        """ % {'AOF': str(AOF)}
        res = self.pool.query(query)
        json = res.serialize(format="json").decode()

        # log.debug(json)
        return json

    #TODO: write Documentation
    @view_config(route_name='api-apps-uris', renderer='json')
    def api_uri_json(self):
        """
        Generates the pool in Json
        :return: json-representation of the AppPool
        """
        # log.debug("called view: ap_get_app_pool_json()")
        query = """
        PREFIX aof: <%(AOF)s>
        SELECT DISTINCT ?label ?uri
        WHERE {
        ?uri rdfs:label ?label ;
            aof:hasInstallableArtifact ?binary .
            OPTIONAL {
            ?uri aof:hasIcon ?icon
            }

        }
        ORDER BY ?name
        """ % {'AOF': str(AOF)}
        res = self.pool.query(query)
        json = res.serialize(format="json").decode()

        # log.debug(json)
        return json


    @view_config(route_name='app-details', renderer='aof:templates/app-details.mako', accept='text/html')
    @RequestPoolURI_Decorator()
    @AppCheckDecorator()
    def page_details(self):
        """
        Generates the Detail-Attributes for an given Request-URI
        :return: dictionary
        """
        self._setTitle('App-Details')
        details = {
            'name': self.pool.get_name(self.uri).__str__(),
            'comment': self.pool.get_description(self.uri).__str__(),
            'icon': self.pool.get_icon_uri(self.uri).__str__(),
            'binary': self.pool.get_install_uri(self.uri).__str__(),
            'has_role': self.pool.has_role(self.uri),
            'has_main_screenshot': self.pool.has_main_screenshot(self.uri),
            'has_other_screenshots': self.pool.has_other_screenshots(self.uri),
            'has_creator': self.pool.has_creator(self.uri),
            'has_entry_points': self.pool.has_entry_points(self.uri),
            'has_exit_points': self.pool.has_exit_points(self.uri)
        }
        if details['has_role']:
            roles = self.pool.get_roles(self.uri)
        else:
            roles = None

        if details['has_creator']:
            creators = self.pool.get_creators(self.uri)
        else:
            creators = None

        if details['has_main_screenshot']:
            main_screenshot = self.pool.get_main_screenshot(self.uri)
        else:
            main_screenshot = None

        if details['has_other_screenshots']:
            screenshots = self.pool.get_other_screenshots(self.uri)
        else:
            screenshots = None

        if details['has_entry_points']:
            entry_points = self.pool.get_entry_points(self.uri)
        else:
            entry_points = None

        if details['has_exit_points']:
            exit_points = self.pool.get_exit_points(self.uri)
        else:
            exit_points = None

        custom_args = {'namespaces': namespaces,
                       'uri': self.uri,
                       'qrcode': self.pool.get_QRCode(details['binary']),
                       'details': details,
                       'roles': roles,
                       'creators': creators,
                       'main_screenshot': main_screenshot,
                       'screenshots': screenshots,
                       'entry_points': entry_points,
                       'exit_points': exit_points,
                       'api_app_ttl_uri':self.build_URI('api-apps-app-details','{URI:.*}',self.uri)+"?format=turtle&content_type=text/plain"
                       # build number is loaded via ajax
                       }
        return self._returnCustomDict(custom_args)


    @RequestPoolURI_Decorator()
    @AppCheckDecorator()
    def _api_details_return(self,format,content_type=None):
        """
        Extracts all tuples for an specific URI out of the Graph
        :param format: desired format of the App-Details i.e. "application/rdf+xml" or "text/turtel"
        :param content_type: desired output medium i.e. "application/rdf+xml" or "text/plain"
        :return:
        """
        ret = ConjunctiveGraph()
        ret = fill_graph_by_subject(self.pool, ret, self.uri)
        ret=ret.serialize(format=format)
        return Response(ret,content_type=content_type)

    @RequestPoolURI_Decorator()
    @view_config(route_name='api-apps-app-version', renderer='json')
    def api_app_version_json(self):
        result={'build_number':self.pool.get_build_number(self.uri)}
        return result

    @view_config(route_name='api-apps-app-details')
    @view_config(route_name='app-details', accept='text/turtle')
    @view_config(route_name='app-details', accept='application/rdf+xml')
    @RequestPoolURI_Decorator()
    def api_app_details(self):
        if self.request.params.has_key('format') or self.request.params.has_key('content_type'):
            format=None
            content_type=None
            if self.request.params.has_key('format'):
                format=self.request.params.getone('format')
            else:
                format='application/rdf+xml'
            if self.request.params.has_key('content_type'):
                content_type=self.request.params.getone('content_type')
            return self._api_details_return(format=format,content_type=content_type)
        elif 'text/turtle' in str(self.request.accept):
            return self._api_details_return(format='turtle',content_type='text/turtle')
        else:
            return self._api_details_return(format='application/rdf+xml',content_type='application/rdf+xml')


    @view_config(route_name='api-apps-app-property', renderer='json')
    @RequestPoolURI_Decorator()
    def api_app_param(self, param = None):
        if param == None:
            param=self.request.matchdict['property']
        response=list()
        for s, p, o in self.pool.triples((self.uri,URIRef(param),None)):
            response.append(o)
        return response

    @view_config(route_name='api-apps-app-apk', renderer='json')
    @RequestPoolURI_Decorator()
    def api_app_apk(self):
        result={'apk_uri':self.pool.get_tuple(self.uri, AOF.hasInstallableArtifact,to_string=True)}
        return result










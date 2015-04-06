import os
import logging
from pyramid.httpexceptions import HTTPNotFound
from pyramid.path import AssetResolver
from pyramid.view import view_config
from pyramid.response import Response, FileResponse
from rdflib import URIRef
from simpleconfigparser import simpleconfigparser
from aof.orchestration.AOFGraph import AOFGraph
from aof.orchestration.AppPool import AppPool
from aof.orchestration.namespaces import AOF, ANDROID
from rdflib.namespace import DC, FOAF, RDF, RDFS

from aof.orchestration import ae_tools

from aof.static.data.static_data import META

config = simpleconfigparser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)+'/aof.conf')

a_resolver = AssetResolver()
static_dir = a_resolver.resolve('aof:static/').abspath()

app_pool = config.Paths.app_ensemble_location

log = logging.getLogger(__name__)

namespaces = {'AOF': AOF, 'ANDROID': ANDROID, 'DC': DC, 'FOAF': FOAF, 'RDF': RDF, 'RDFS': RDFS}

@view_config(route_name='home', renderer='templates/home.mako')
def home_view(request):
    ap = AppPool.Instance()
    number_of_apps = str(ap.get_number_of_apps())
    number_of_ae = str(ae_tools.getNumberOfAE())
    g = AOFGraph.Instance()
    unique_triples = str(g.__len__())
    return {'meta': META,
            'page_title': 'AOF Home',
            'number_of_apps': number_of_apps,
            'number_of_ae': number_of_ae,
            'unique_triples': unique_triples}

@view_config(route_name='documentation', renderer='templates/documentation.mako')
def documentation_view(request):
    return {'meta': META,
            'page_title': 'Documentation'}

@view_config(route_name='documentation-docs', renderer='templates/documentation-docs.mako')
def documentation_docs_view(request):
    document = request.matchdict['document']
    if document == "app-description_specification":
        content = open(os.path.join(static_dir,'doc','PLT-Bericht App-Description Specification v001.docx.html')).read()
    elif document == "app-ensemble_specification":
        content = open(os.path.join(static_dir,'doc','PLT-Bericht App-Ensemble Specification v001.docx.html')).read()

    return {'meta': META,
            'page_title': 'Documentation',
            'content': content}

class AppPoolViews():
    def __init__(self, request):
        self.request = request
        #log.debug("Called __init__() of class AppPoolViews()")

    @view_config(route_name='app-pool', renderer='templates/app-pool.mako')
    def ap_pool_view(self):
        apps = list()
        ap = AppPool.Instance()
        app_uris = ap.get_app_uris()
        for app_uri in app_uris:
            app = {
                'uri': app_uri,
                'name': ap.get_name(app_uri),
                'icon': ap.get_icon_uri(app_uri),
                'binary': ap.get_binary_uri(app_uri)
            }
            apps.append(app)

        apps = sorted(apps, key=lambda app: (app['name'], app['uri']))

        return {'meta': META,
                'page_title': 'App-Pool',
                'apps': apps
        }

    @view_config(route_name='app-details', renderer='templates/app-details.mako')
    def ap_app_details_view(self):
        if not self.request.params.has_key('URI'):
            return Response('The parameter "URI" was not supplied. Please provide the URI of the App for which you want to display the details.')
        else:
            if len(self.request.params.getall('URI')) > 1:
                return Response('More than one URI was supplied. Please supply exactly 1 URI.')
            else:
                uri = self.request.params.getone('URI')
                if uri == "":
                    return Response('Value of the "URI"-parameter was empty. Please provide the URI of the App.')

        ap = AppPool.Instance()

        if ap.is_android_app(URIRef(uri)) != True:
            return Response("The app '%s' doesn't seem to be an Android App. Currently only Android Apps are supported." % uri)

        details = {
            'name': ap.get_name(URIRef(uri)).__str__(),
            'comment': ap.get_description(URIRef(uri)).__str__(),
            'icon': ap.get_icon_uri(URIRef(uri)).__str__(),
            'binary': ap.get_binary_uri(URIRef(uri)).__str__(),
            'has_role': ap.has_role(URIRef(uri)),
            'has_main_screenshot': ap.has_main_screenshot(URIRef(uri)),
            'has_other_screenshots': ap.has_other_screenshots(URIRef(uri)),
            'has_creator': ap.has_creator(URIRef(uri)),
            'has_entry_points': ap.has_entry_points(URIRef(uri)),
            'has_exit_points': ap.has_exit_points(URIRef(uri))
        }
        if details['has_role']:
            roles = ap.get_roles(URIRef(uri))
        else:
            roles = None

        if details['has_creator']:
            creators = ap.get_creators(URIRef(uri))
        else:
            creators = None

        if details['has_main_screenshot']:
            main_screenshot = ap.get_main_screenshot(URIRef(uri))
        else:
            main_screenshot = None

        if details['has_other_screenshots']:
            screenshots = ap.get_other_screenshots(URIRef(uri))
        else:
            screenshots = None

        if details['has_entry_points']:
            entry_points = ap.get_entry_points(URIRef(uri))
        else:
            entry_points = None

        if details['has_exit_points']:
            exit_points = ap.get_exit_points(URIRef(uri))
        else:
            exit_points = None

        return {'meta': META,
                'page_title': 'App-Details',
                'namespaces': namespaces,
                'uri': uri,
                'details': details,
                'roles': roles,
                'creators': creators,
                'main_screenshot': main_screenshot,
                'screenshots': screenshots,
                'entry_points': entry_points,
                'exit_points': exit_points
        }
    # Returns information on the App-Pool as JSON

    @view_config(route_name='api-ap-json', renderer='json')
    def api_ap_json_view(self):
        #log.debug("called view: ap_get_app_pool_json()")
        query = """
        PREFIX aof: <%(AOF)s>
        SELECT DISTINCT *
        WHERE {
        ?uri rdfs:label ?name ;
            aof:currentBinary ?binary .
            OPTIONAL {
            ?uri aof:hasIcon ?icon
            }

        }
        ORDER BY ?name
        """ % {'AOF': str(AOF)}
        ap = AppPool.Instance()
        res = ap.query(query)
        json = res.serialize(format="json").decode()

        # log.debug(json)
        return {'json': json}
    @view_config(route_name='action-update-app-pool')
    def action_update_app_pool_view(self):
        a = AssetResolver()
        path = a.resolve('aof:static/App-Pool/pool.ttl').abspath()
        ap = AppPool.Instance()
        ap.update_app_pool(path, format="turtle")
        res = AppPool.Instance().triples((None, AOF.hasAppDescription, None))
        resp = str(len(list(res)))
        return Response(resp)


class AppEnsembleViews():


    ae_dict = None

    def __init__(self, request):
        self.request = request
        if not type(self).ae_dict:
            type(self).ae_dict = ae_tools.initializeExistingAE()

    @view_config(route_name='app-ensembles', renderer='templates/ae.mako')
    def app_ensembles_view(request):
        return {'meta': META,
                'page_title': 'App-Ensembles'}

    @view_config(route_name='ae-details', renderer='templates/ae-details.mako')
    def ae_details_view(self):
        if not self.request.params.has_key('URI'):
            return Response('The parameter "URI" was not supplied. Please provide the URI of the App-Ensemble for which you want to display the details.')
        else:
            if len(self.request.params.getall('URI')) > 1:
                return Response('More than one URI was supplied. Please supply exactly 1 URI.')
            else:
                ae_uri = self.request.params.getone('URI')
                if ae_uri == "":
                    return Response('Value of the "URI"-parameter was empty. Please provide the URI of the App-Ensemble.')

        if ae_uri in self.ae_dict:
            ae = self.ae_dict[ae_uri]
            ae_apps = ae.getRequiredApps().bindings
            return {
                'ae_path': ae.ae_pkg_path,
                'ae_uri': ae_uri,
                'ae_has_bpm': ae.has_bpm(),
                'ae_apps': ae_apps,
                'meta': META,
                'page_title': 'App-Ensemble Details'
            }
        else:
            return HTTPNotFound('The App-Ensemble "%s" could not be found.' % ae_uri)

    @view_config(route_name='ae-visualize-bpm', renderer='templates/ae-visualize-bpm.mako')
    def ae_visualize_bpm_view(self):
        if not self.request.params.has_key('URI'):
            return Response('The parameter "URI" was not supplied. Please provide the URI of the App-Ensemble for which you want to visualize the BPM.')
        else:
            if len(self.request.params.getall('URI')) > 1:
                return Response('More than one URI was supplied. Please supply exactly 1 URI.')
            else:
                ae_uri = self.request.params.getone('URI')
                if ae_uri == "":
                    return Response('Value of the "URI"-parameter was empty. Please provide the URI of the App-Ensemble.')
        if ae_uri in self.ae_dict:
            ae = self.ae_dict[ae_uri]

            return {
                'ae_path': ae.ae_pkg_path,
                'ae_uri': ae_uri,
                'ae_has_bpmn': ae.has_bpm(),
                'meta': META,
                'page_title': 'App-Ensemble Details'
            }
        else:
            response = HTTPNotFound('The App-Ensemble "%s" could not be found.' % ae_uri)

    @view_config(route_name='ae-bpmn')
    def ae_get_bpmn_view(self):
        if not self.request.params.has_key('URI'):
            return Response('The parameter "URI" was not supplied. Please provide the URI of the App-Ensemble for which you want to retrieve the BPMN.')
        else:
            if len(self.request.params.getall('URI')) > 1:
                return Response('More than one URI was supplied. Please supply exactly 1 URI.')
            else:
                ae_uri = self.request.params.getone('URI')
                if ae_uri == "":
                    return Response('Value of the "URI"-parameter was empty. Please provide the URI of the App-Ensemble.')

        if ae_uri in self.ae_dict:
            ae = self.ae_dict[ae_uri]
            bpmn = ae.get_bpm()
            response = Response(
                body=bpmn,
                request=self.request,
                content_type='txt/xml'
            )
            response.content_disposition = 'attachement; filename="'+ae_uri+".bpmn"
        else:
            response = HTTPNotFound('The App-Ensemble "%s" could not be found.' % ae_uri)
        return response
    # Returns a json representation of all App-Ensembles + some additional info

    @view_config(route_name='api-ae-json',renderer='json')
    def api_ae_json_view(self):
        ae_info = dict()
        try:
            for key, ae in self.ae_dict.items():
                path = ae.ae_pkg_path
                apps = ae.getRequiredApps().serialize(format='json').decode()
                ae_info[key] = {'uri': key, 'path': path, 'apps': apps}
        except AttributeError:
            ae_info[key] = {'uri': key, 'path': path, 'apps': {}}
        return {'json': ae_info}

    @view_config(route_name='api-get-ae-pkg')
    def ae_get_ae_pkg_view(self):
        if not self.request.params.has_key('URI'):
            return Response('The parameter "URI" was not supplied. Please provide the URI of the App-Ensemble for which you want to visualize the BPM.')
        else:
            if len(self.request.params.getall('URI')) > 1:
                return Response('More than one URI was supplied. Please supply exactly 1 URI.')
            else:
                ae_uri = self.request.params.getone('URI')
                if ae_uri == "":
                    return Response('Value of the "URI"-parameter was empty. Please provide the URI of the App-Ensemble.')

        if ae_uri in self.ae_dict:
            ae = self.ae_dict.get(ae_uri)
            response = FileResponse(
                ae.ae_pkg_path,
                request=self.request,
                content_type='application/vnd.aof.package-archive'
            )
            response.content_disposition = 'attachement; filename="'+ae_uri+".ae"
        else:
            response = HTTPNotFound('The App-Ensemble "%s" could not be found.' % ae_uri)

        return response

    @view_config(route_name='action-update-ap-ensembles')
    def action_update_app_ensembles_view(self):
        type(self).ae_dict = ae_tools.initializeExistingAE()
        resp = str(len(self.ae_dict))
        return Response(resp)

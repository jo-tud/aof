import os
import logging
from pyramid.httpexceptions import HTTPNotFound
from pyramid.path import AssetResolver
from pyramid.view import view_config
from pyramid.response import Response, FileResponse
from simpleconfigparser import simpleconfigparser
from aof.orchestration.AOFGraph import AOFGraph
from aof.orchestration.AppPool import AppPool
from aof.orchestration.namespaces import AOF, ADL

from aof.orchestration import ae_tools

from aof.static.data.static_data import META

config = simpleconfigparser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)+'/aof.conf')

a_resolver = AssetResolver()
static_dir = a_resolver.resolve('aof:static/').abspath()

app_pool = config.Paths.app_ensemble_location

log = logging.getLogger(__name__)

@view_config(route_name='home', renderer='templates/home.mako')
def home_view(request):
    ap = AppPool.Instance()
    number_of_apps = str(ap.getNumberOfApps())
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
        apps = dict()
        apps = ap.query(query)


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
                app_uri = self.request.params.getone('URI')
                if app_uri == "":
                    return Response('Value of the "URI"-parameter was empty. Please provide the URI of the App.')

        isAndroidAppQuery = ("""
            # AOF PREFIXES
            PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>

            ASK
            WHERE {
                    <%(uri)s> a aof:AndroidApp .
            }
        """) % {'uri': app_uri}

        appDetailsQuery = ("""
            # AOF PREFIXES
            PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>

            SELECT *
            WHERE {
                # This is only for Android apps
                <%(uri)s> a aof:AndroidApp ;

                    # Label & comment
                    rdfs:label ?label ;
                    rdfs:comment ?comment ;
                    aof:currentBinary ?binary .

                # Role
                OPTIONAL {
                    <%(uri)s> aof:hasRole ?role .
                }

                # Main screenshot
                OPTIONAL {
                    <%(uri)s> a aof:AndroidApp ;
                        aof:MainScreenshot [
                        aof:hasScreenshot ?main_screenshot_uri ;
                        aof:hasScreenshotThumbnail ?main_screenshot_thumb_uri
                    ] .
                    OPTIONAL {
                        <%(uri)s> a aof:AndroidApp ;
                            aof:MainScreenshot [
                            rdfs:comment ?main_screenshot_comment
                        ] .
                    }
                }

                # Main screenshot
                OPTIONAL {
                    <%(uri)s> aof:hasIcon ?icon .
                }

                # Creator
                <%(uri)s> dc:creator ?creator .
                ?creator foaf:name ?creator_name ;
                    foaf:mbox ?creator_mbox ;
                    foaf:homepage ?creator_homepage .
            }
        """) % {'uri': app_uri}

        # Get all additional screenshots
        screenshotQuery = ("""
            # AOF PREFIXES
            PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>

            SELECT *
            WHERE {
                OPTIONAL {
                    <%(uri)s> a aof:AndroidApp ;
                        aof:Screenshot [
                        aof:hasScreenshot ?main_screenshot_uri ;
                        aof:hasScreenshotThumbnail ?main_screenshot_thumb_uri
                    ] .
                    OPTIONAL {
                        <%(uri)s> a aof:AndroidApp ;
                            aof:Screenshot [
                            rdfs:comment ?main_screenshot_comment
                        ] .
                    }
                }
            }
        """) % {'uri': app_uri}

        # Get details for all entry points
        entryPointsQuery = ("""
            # AOF PREFIXES
            PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
            PREFIX android: <http://schemas.android.com/apk/res/android>

            SELECT DISTINCT *
            WHERE {
                OPTIONAL {
                    <%(uri)s> aof:providesEntryPoint ?entryPoint .
                    BIND (android:action AS ?type)

                    ?entryPoint a android:action ;
                        rdfs:label ?label ;
                        rdfs:comment ?comment ;
                        android:name ?androidActionName .
                }
            }
            ORDER BY ?label
        """) % {'uri': app_uri}

        # Get all inputs for all entry points
        entryPointsInputsQuery = ("""
            # AOF PREFIXES
            PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
            PREFIX android: <http://schemas.android.com/apk/res/android>

            SELECT DISTINCT ?entryPoint ?input ?isRequired ?datatype ?androidExtraName ?type
            WHERE {
                OPTIONAL {
                    <%(uri)s> aof:providesEntryPoint ?entryPoint .
                    BIND (android:extra AS ?type)

                    ?entryPoint a android:action ;
                        aof:hasInput ?input .

                    ?input a android:extra ;
                        aof:isRequired ?isRequired ;
                        aof:datatype ?datatype ;
                        android:name ?androidExtraName .
                }
            }
            ORDER BY ?androidExtraName
        """) % {'uri': app_uri}

        # Get details for all exit points
        exitPointsQuery = ("""
            # AOF PREFIXES
            PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
            PREFIX android: <http://schemas.android.com/apk/res/android>

            SELECT *
            WHERE {
                OPTIONAL {
                    <%(uri)s> aof:providesExitPoint ?exitPoint .

                    ?exitPoint a android:action ;
                        a ?type ;
                        rdfs:label ?label ;
                        rdfs:comment ?comment .
                }
            }
        """) % {'uri': app_uri}

        # Get all inputs for all entry points
        exitPointsOutputsQuery = ("""
            # AOF PREFIXES
            PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
            PREFIX android: <http://schemas.android.com/apk/res/android>

            SELECT ?entryPoint ?output ?isGuaranteed ?datatype ?androidExtraName
            WHERE {
                OPTIONAL {
                    <%(uri)s> aof:providesEntryPoint ?entryPoint .

                    ?entryPoint a android:action ;
                        aof:hasOutput ?output .

                    ?output a android:extra ;
                        aof:isGuaranteed ?isGuaranteed ;
                        aof:datatype ?datatype ;
                        android:name ?androidExtraName .
                }
            }
        """) % {'uri': app_uri}

        ap = ap = AppPool.Instance()

        # Execute queries
        isAndroidApp = ap.query(isAndroidAppQuery).askAnswer

        if isAndroidApp != True:
            return Response("The app '%s' doesn't seem to be an Android App. Currently only Android Apps are supported." % app_uri)

        app_details = ap.query(appDetailsQuery).bindings[0]
        screenshots = ap.query(screenshotQuery)
        entry_points = ap.query(entryPointsQuery)
        entry_points_inputs = ap.query(entryPointsInputsQuery)
        exit_points = ap.query(exitPointsQuery)
        exit_points_outputs = ap.query(exitPointsOutputsQuery)

        return {'meta': META,
                'page_title': 'App-Details',
                'app_uri': app_uri,
                'app_details': app_details,
                'screenshots': screenshots,
                'entry_points': entry_points,
                'entry_points_inputs': entry_points_inputs,
                'exit_points': exit_points,
                'exit_points_outputs': exit_points_outputs
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

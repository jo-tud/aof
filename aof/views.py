from aof.orchestration.AppPool import AppPool
from aof.orchestration.AppEnsembleManager import AppEnsembleManager
from aof.orchestration.AOFGraph import AOFGraph

import os
import logging
from functools import wraps

from pyramid.view import view_config
from pyramid.response import Response, FileResponse
from rdflib import URIRef
from pyramid.httpexceptions import HTTPNotFound
from pyramid.path import AssetResolver

from aof.orchestration.namespaces import AOF, ANDROID
from rdflib.namespace import DC, FOAF, RDF, RDFS

a_resolver = AssetResolver()
namespaces = {'AOF': AOF, 'ANDROID': ANDROID, 'DC': DC, 'FOAF': FOAF, 'RDF': RDF, 'RDFS': RDFS}
log = logging.getLogger(__name__)


class RequestPoolURI_Decorator(object):
    """
    Decorator Function:
    - Was an URI supplied
    - Was only one URI supplied
    - Was an URI supplied but the value empty
    - Does the supplied uri has an reference in the AppPool or AppEnsembleManager

    # Add this to Methods which use URIs to get Information about Elements out of the appPool or AppEnsembleManager
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
                        elif isinstance(self.pool, AppEnsembleManager):
                            if self.uri in self.pool:
                                self.uri = URIRef(self.uri)
                                return f(self, *args, **kwargs)
                            else:
                                return HTTPNotFound(
                                    'The uri "%s" could not be found in the AppEnsemblePool.' % self.uri)
                        else:
                            return log.error(
                                'URIExistDecorator was called without an AppPool or an AppEnsembleManager. The given object was an instance of {} and the pool was of type {}'.format(
                                    type(self), type(self.pool)))

                        return f(self, *args, **kwargs)

        return wrapper


class AppCheckDecorator(object):
    """
    Decorator function:
    - Is the URI of the object the URI of an Android-App

    # Use this only for Methods only with an AppPool as class-attibute pool
    """

    def __call__(self, f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if (hasattr(self, "pool") and isinstance(self.pool, AppPool))
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


class DocumentExistsDecorator(object):
    """
    Decorator function:
    - Is there an document which matches the supplied URI

    # Use this only for subclasse of DocumentationViews
    """

    def __call__(self, f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if (issubclass(self, DocumentationViews)):
                document = self.request.matchdict['document']
                doc_path = os.path.join(self.docs_path, document)
                if os.path.exists(doc_path):
                    return f(self, *args, **kwargs)
                else:
                    return HTTPNotFound('The resource "%s" could not be found within the Documentation.' % document)
            else:
                import inspect

                log.info(
                    "DocumentExistsDecorator is used for a method ({}) which doesn't belong to the Documentation-Context!".format(
                        inspect.stack()[1][3]))
                return HTTPNotFound('The Documentation-Page could not be opened.')

        return wrapper


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


class PageViews(AbstractViews):
    def __init__(self, context, request):
        """
        Super-Class for all Pages. Adds the pool and the page-title attribute
        """
        super(PageViews, self).__init__(context, request)
        self.pool = None
        self.page_title = None
        import ast

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

    @view_config(route_name='home', renderer='templates/home.mako')
    def page_home(self):
        """
        Generates the parameters for the Home-page
        """
        self._setTitle('AOF Home')
        ap = AppPool.Instance()
        aem = AppEnsembleManager.Instance()
        number_of_apps = str(ap.get_number_of_apps())
        number_of_ae = str(len(aem))
        g = AOFGraph.Instance()
        unique_triples = str(g.__len__())
        custom_args = {'number_of_apps': number_of_apps,
                       'number_of_ae': number_of_ae,
                       'unique_triples': unique_triples}
        return self._returnCustomDict(custom_args)


class AppPoolViews(PageViews):
    def __init__(self, context, request):
        """
        Class with all AppPool-Pages and -Actions
        """
        super(AppPoolViews, self).__init__(context, request)
        self.pool = AppPool.Instance()

    @view_config(route_name='app-pool', renderer='templates/app-pool.mako')
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
                'name': self.pool.get_name(app_uri),
                'icon': self.pool.get_icon_uri(app_uri),
                'binary': self.pool.get_install_uri(app_uri)
            }
            apps.append(app)

        apps = sorted(apps, key=lambda app: (app['name'], app['uri']))

        custom_args = {'apps': apps}
        return self._returnCustomDict(custom_args)

    @view_config(route_name='action-update-app-pool')
    def action_update(self):
        """
        Action: Update the AppPool from current AppPool definition
        :return: Response Object with number of Apps
        """
        self.pool.add_apps_from_app_pool_definition(source=None, format='turtle')
        res = str(self.pool.get_number_of_apps())
        return Response(res)

    @view_config(route_name='api-ap-json', renderer='json')
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
        return {'json': json}

    @view_config(route_name='app-details', renderer='templates/app-details.mako')
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
                       'details': details,
                       'roles': roles,
                       'creators': creators,
                       'main_screenshot': main_screenshot,
                       'screenshots': screenshots,
                       'entry_points': entry_points,
                       'exit_points': exit_points
                       }
        return self._returnCustomDict(custom_args)


class AppEnsembleViews(PageViews):
    """
    Class with all AppEnsemble-Pages and -Actions
    """

    def __init__(self, context, request):
        super(AppEnsembleViews, self).__init__(context, request)
        self.pool = AppEnsembleManager.Instance()

    @view_config(route_name='app-ensembles', renderer='templates/ae.mako')
    def page_overview(self):
        """
        Generates the parameters for the AppEnsemble-Homepage
        """
        self._setTitle('App-Ensembles')
        return self._returnCustomDict()

    @view_config(route_name='api-ae-json', renderer='json')
    def api_json(self):
        """
        Generates the pool in Json
        :return: json-representation of the AppEnsemble-Pool
        """
        ae_info = dict()
        try:
            for key in self.pool.get_all_AppEnsembles():
                ae = self.pool.get_AppEnsemble(key)
                path = ae.ae_pkg_path
                apps = ae.getRequiredApps().serialize(format='json').decode()
                ae_info[key] = {'uri': key, 'path': path, 'apps': apps}
        except AttributeError:
            ae_info[key] = {'uri': key, 'path': path, 'apps': {}}
        return {'json': ae_info}

    @view_config(route_name='action-update-ap-ensembles')
    def action_update(self):
        """
        Action: Update the AppEnsemblePool from current AppEnsemble-directory
        :return: Response Object with number of Apps
        """
        self.pool.reload()
        resp = str(len(self.pool))
        return Response(resp)

    @view_config(route_name='ae-details', renderer='templates/ae-details.mako')
    @RequestPoolURI_Decorator()
    def page_details(self):
        """
        Generates the Detail-Attributes for an given Request-URI
        :return: dictionary
        """
        self._setTitle('App-Ensemble Details')
        ae = self.pool.get_AppEnsemble(self.uri)

        ae_apps = ae.getRequiredApps().bindings
        custom_args = {
            'ae_path': ae.ae_pkg_path,
            'ae_uri': self.uri,
            'ae_has_bpm': ae.has_bpm(),
            'ae_apps': ae_apps
        }
        return self._returnCustomDict(custom_args)

    @view_config(route_name='ae-visualize-bpm', renderer='templates/ae-visualize-bpm.mako')
    @RequestPoolURI_Decorator()
    def page_visualize_bpm(self):
        """
        Generates the BPMN-Visualisation Page
        :return: dictionary
        """
        self._setTitle('App-Ensemble Details | BPMN')
        ae = self.pool.get_AppEnsemble(self.uri)
        custom_args = {
            'ae_path': ae.ae_pkg_path,
            'ae_uri': self.uri,
            'ae_has_bpmn': ae.has_bpm()
        }
        return self._returnCustomDict(custom_args)

    @view_config(route_name='ae-bpmn')
    @RequestPoolURI_Decorator()
    def action_get_bpmn_data(self):
        """
        Generates the BPMN-Data for visulisation
        :return: Response with the BPMN-xml
        """
        ae = self.pool.get_AppEnsemble(self.uri)
        bpmn = ae.get_bpm()
        response = Response(
            body=bpmn,
            request=self.request,
            content_type='txt/xml'
        )
        response.content_disposition = 'attachement; filename="' + str(self.uri) + ".bpmn"
        return response

    @view_config(route_name='api-get-ae-pkg')
    @RequestPoolURI_Decorator()
    def action_get_ae_pkg(self):
        """
        Generates the AppEnsemble-package for downloading
        :return: Response with AppEnsemble-package
        """
        ae = self.pool.get_AppEnsemble(self.uri)
        response = FileResponse(
            ae.ae_pkg_path,
            request=self.request,
            content_type='application/vnd.aof.package-archive'
        )
        response.content_disposition = 'attachement; filename="' + str(self.uri) + ".ae"
        return response


class DocumentationViews(PageViews):
    def __init__(self, context, request):
        """
        Class with all Documentation-Pages and -Actions
        """
        super(DocumentationViews, self).__init__(context, request)

        if request.registry is not None:
            self.docs_path = request.registry.settings['documentation_docs_path']
        else:
            self.docs_path = "aof:resources/docs"

        self.docs_path = AssetResolver().resolve(self.docs_path).abspath()

    @view_config(route_name='documentation', renderer='templates/documentation.mako')
    def page_overview(self):
        """
        Documentation-Homepage with indexes the docs-path and shows all the accessible-files (HTML,LINK,PDF)
        :return: dictionary
        """
        self._setTitle('Documentation')

        def recursive_folder_dict(basepath, root):
            structure = list()
            allowed_doc_types = ('HTML', 'PDF', 'LINK')
            for file in os.listdir(basepath):
                if os.path.isdir(os.path.join(basepath, file)):
                    structure.append(
                        {"name": file, "children": recursive_folder_dict(os.path.join(basepath, file), root)})
                else:
                    tmp_name = os.path.splitext(file)
                    key = tmp_name[1].replace(".", "", 1).upper()
                    if key in allowed_doc_types:
                        if key == "HTML":
                            path = "/docs/"
                        elif key == "LINK":
                            path = "/redirect/"
                        else:
                            path = "/resources/"
                        path += os.path.join(basepath, file).replace(root + "\\", "").replace("\\", "/")
                        for idx, s in enumerate(structure):
                            if s["name"] == tmp_name[0]:
                                s['resources'].update({key: path})
                                structure[idx] = s
                                break
                        else:
                            structure.append({"name": tmp_name[0], "children": None, 'resources': {key: path}})
            return structure

        basepath = self.docs_path
        structure = recursive_folder_dict(basepath, basepath)

        custom_args = {'structure': structure}
        return self._returnCustomDict(custom_args)

    @view_config(route_name='documentation-docs', renderer='templates/documentation-docs.mako')
    @DocumentExistsDecorator()
    def page_html_view(self):
        """
        Shows a specific Documentation-document in HTML
        :return: dictionary
        """
        self._setTitle('Documentation')
        document = self.request.matchdict['document']
        content = open(os.path.join(self.docs_path, self.request.matchdict['document'])).read()

        custom_args = {'content': content}
        return self._returnCustomDict(custom_args)

    @view_config(route_name='documentation-resource')
    @DocumentExistsDecorator()
    def page_resource_response(self):
        """
        Shows a specific Documentation-document in PDF or other downloadable Mime-types
        :return: FileResponse with the document
        """
        document = self.request.matchdict['document']
        response = FileResponse(
            os.path.join(self.docs_path, document),
            request=self.request
        )
        return response

    @view_config(route_name='documentation-redirect')
    def page_redirect_response(self):
        """
        Generates an HTTP-REDIRECT to the requested URL
        :return: HTTPFound
        """
        from pyramid.httpexceptions import HTTPFound

        content = open(os.path.join(self.docs_path, self.request.matchdict['document'])).read()
        return HTTPFound(location=content)

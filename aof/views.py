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

from webob.multidict import MultiDict

from aof.static.data.static_data import META


a_resolver = AssetResolver()
static_dir = a_resolver.resolve('aof:static/').abspath()
namespaces= {'AOF': AOF, 'ANDROID': ANDROID, 'DC': DC, 'FOAF': FOAF, 'RDF': RDF, 'RDFS': RDFS}
log = logging.getLogger(__name__)


class URICheckDecorator(object):
    def __call__(self, f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if not self.request.params.has_key('URI'):
                return Response('The parameter "URI" was not supplied. Please provide the URI of the App-Ensemble for which you want to display the details.')
            else:
                if len(self.request.params.getall('URI')) > 1:
                    return Response('More than one URI was supplied. Please supply exactly 1 URI.')
                else:
                    uri = self.request.params.getone('URI')
                    if uri == "":
                        return Response('Value of the "URI"-parameter was empty. Please provide the URI of the App-Ensemble.')
                    else:
                        self.uri=URIRef(uri)
                        return f(self, *args, **kwargs)
        return wrapper

class URIExistDecorator(object):
    def __call__(self, f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if isinstance(self.pool,AppPool):
                if self.pool.in_pool(self.uri):
                    return f(self, *args, **kwargs)
                else:
                    return HTTPNotFound('The uri "%s" could not be found in the AppPool.' % self.uri)
            elif isinstance(self.pool,AppEnsembleManager):
                if self.uri in self.pool:
                    return f(self, *args, **kwargs)
                else:
                    return HTTPNotFound('The uri "%s" could not be found in the AppEnsemblePool.' % self.uri)
            else:
                return log.error('URIExistDecorator was called without an AppPool or an AppEnsembleManager. The given object was an instance of {} and the pool was of type {}'.format(type(self),type(self.pool)))
        return wrapper

class AppCheckDecorator(object):
    def __call__(self, f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if self.pool.is_android_app(self.uri) != True:
                return Response("The app '%s' doesn't seem to be an Android App. Currently only Android Apps are supported." % self.uri)
            else:
                return f(self, *args, **kwargs)
        return wrapper


class AbstractViews():
    def __init__(self,context, request):
        self.context=context
        self.request=request

    def _returnCustomDict(self,*args):
        return_args=dict()
        for arg in args:
            if arg is not None:
                return_args.update(arg)
        return return_args

class PageViews(AbstractViews):
    def __init__(self, context, request):
        super(PageViews, self).__init__(context, request)
        self.pool=None
        self.page_title="Page Title not defined"
        import ast
        self.meta=ast.literal_eval(self.request.registry.settings['META'])

    def _returnCustomDict(self, *args):
        custom_args={'meta': self.meta,'page_title': self.page_title}
        return super(PageViews, self)._returnCustomDict(custom_args,*args)

    def _setTitle(self,value):
        self.page_title=value

    @view_config(route_name='home', renderer='templates/home.mako')
    def page_home(self):
        self._setTitle('AOF Home')
        ap = AppPool.Instance()
        aem=AppEnsembleManager.Instance()
        number_of_apps = str(ap.get_number_of_apps())
        number_of_ae = str(len(aem))
        g = AOFGraph.Instance()
        unique_triples = str(g.__len__())
        custom_args= {'number_of_apps': number_of_apps,
                'number_of_ae': number_of_ae,
                'unique_triples': unique_triples}
        return self._returnCustomDict(custom_args)


class AppPoolViews(PageViews):
    def __init__(self, context, request):
        super(AppPoolViews, self).__init__(context, request)
        self.pool=AppPool.Instance()
    
    @view_config(route_name='app-pool', renderer='templates/app-pool.mako')
    def page_overview(self):
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

        custom_args={'apps': apps}
        return self._returnCustomDict(custom_args)

    @view_config(route_name='action-update-app-pool')
    def action_update(self):
        self.pool.add_apps_from_app_pool_definition(source=None,format='turtle')
        res = str(self.pool.get_number_of_apps())
        return Response(res)

    @view_config(route_name='api-ap-json', renderer='json')
    def api_json(self):
        #log.debug("called view: ap_get_app_pool_json()")
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
    @URICheckDecorator()
    @URIExistDecorator()
    @AppCheckDecorator()
    def page_details(self):
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

        custom_args={'namespaces': namespaces,
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
    def __init__(self, context, request):
        super(AppEnsembleViews, self).__init__(context, request)
        self.pool=AppEnsembleManager.Instance()
        
    @view_config(route_name='app-ensembles', renderer='templates/ae.mako')
    def page_overview(self):
        self._setTitle('App-Ensembles')
        return self._returnCustomDict()


    @view_config(route_name='api-ae-json',renderer='json')
    def api_json(self):
        ae_info = dict()
        try:
            for key in self.pool.get_all_AppEnsembles():
                ae=self.pool.get_AppEnsemble(key)
                path = ae.ae_pkg_path
                apps = ae.getRequiredApps().serialize(format='json').decode()
                ae_info[key] = {'uri': key, 'path': path, 'apps': apps}
        except AttributeError:
            ae_info[key] = {'uri': key, 'path': path, 'apps': {}}
        return {'json': ae_info}

    @view_config(route_name='action-update-ap-ensembles')
    def action_update(self):
        self.pool.reload()
        resp = str(len(self.pool))
        return Response(resp)


    @view_config(route_name='ae-details', renderer='templates/ae-details.mako')
    @URICheckDecorator()
    @URIExistDecorator()
    def page_details(self):
        self._setTitle('App-Ensemble Details')
        ae = self.pool.get_AppEnsemble(self.uri)

        ae_apps = ae.getRequiredApps().bindings
        custom_args= {
                    'ae_path': ae.ae_pkg_path,
                    'ae_uri': self.uri,
                    'ae_has_bpm': ae.has_bpm(),
                    'ae_apps': ae_apps
                }
        return self._returnCustomDict(custom_args)

    @view_config(route_name='ae-visualize-bpm', renderer='templates/ae-visualize-bpm.mako')
    @URICheckDecorator()
    @URIExistDecorator()
    def page_visualize_bpm(self):
        self._setTitle('App-Ensemble Details')
        ae = self.pool.get_AppEnsemble(self.uri)
        custom_args= {
                    'ae_path': ae.ae_pkg_path,
                    'ae_uri': self.uri,
                    'ae_has_bpmn': ae.has_bpm()
                }
        return self._returnCustomDict(custom_args)


    @view_config(route_name='ae-bpmn')
    @URICheckDecorator()
    @URIExistDecorator()
    def page_get_bpmn(self):
        ae = self.pool.get_AppEnsemble(self.uri)
        bpmn = ae.get_bpm()
        response = Response(
                    body=bpmn,
                    request=self.request,
                    content_type='txt/xml'
                )
        response.content_disposition = 'attachement; filename="'+str(self.uri)+".bpmn"
        return response


    @view_config(route_name='api-get-ae-pkg')
    @URICheckDecorator()
    @URIExistDecorator()
    def page_get_ae_pkg(self):
        ae = self.pool.get_AppEnsemble(self.uri)
        response = FileResponse(
                ae.ae_pkg_path,
                request=self.request,
                content_type='application/vnd.aof.package-archive'
            )
        response.content_disposition = 'attachement; filename="'+str(self.uri)+".ae"
        return response


class DocumentationViews(PageViews):
    def __init__(self, context, request):
        super(DocumentationViews, self).__init__(context, request)

        if request.registry is not None:
            self.docs_path=request.registry.settings['documentation_docs_path']
        else:
            self.docs_path="aof:resources/docs"

        self.docs_path=AssetResolver().resolve(self.docs_path).abspath()

    @view_config(route_name='documentation', renderer='templates/documentation.mako')
    def page_overview(self):
        self._setTitle('Documentation')

        def recursive_folder_dict(basepath,root):
            structure=list()
            allowed_doc_types=('HTML','PDF','LINK')
            for file in os.listdir(basepath):
                if os.path.isdir(os.path.join(basepath,file)):
                    structure.append({"name" : file, "children":recursive_folder_dict(os.path.join(basepath,file),root)})
                else:
                    tmp_name=os.path.splitext(file)
                    key=tmp_name[1].replace(".","",1).upper()
                    if key in allowed_doc_types:
                        if key=="HTML":
                            path="/docs/"
                        elif key=="LINK":
                            path="/redirect/"
                        else:
                            path="/resources/"
                        path +=os.path.join(basepath,file).replace(root+"\\","").replace("\\","/")
                        for idx,s in enumerate(structure):
                            if s["name"]==tmp_name[0]:
                                s['resources'].update({key :path})
                                structure[idx] = s
                                break
                        else:
                            structure.append({"name" : tmp_name[0], "children":None, 'resources':{key:path}})
            return structure


        basepath=self.docs_path
        structure=recursive_folder_dict(basepath,basepath)

        custom_args= {'structure': structure}
        return self._returnCustomDict(custom_args)

    @view_config(route_name='documentation-docs', renderer='templates/documentation-docs.mako')
    def page_doc_view(self):
        self._setTitle('Documentation')
        document = self.request.matchdict['document']
        if document == "app-description_specification.html":
            content = open(os.path.join(self.docs_path,'AOF Language Specification v002.docx.html')).read()
        else:
            content = open(os.path.join(self.docs_path,self.request.matchdict['document'])).read()

        custom_args= {'content': content}
        return self._returnCustomDict(custom_args)


    @view_config(route_name='documentation-resource')
    def page_resource_response(self):
        document = self.request.matchdict['document']
        response = FileResponse(
                os.path.join(self.docs_path,document),
                request=self.request
            )
        return response

    @view_config(route_name='documentation-redirect')
    def page_redirect_response(self):
        from pyramid.httpexceptions import HTTPFound
        content = open(os.path.join(self.docs_path,self.request.matchdict['document'])).read()
        return HTTPFound(location=content)










import os
import logging
from pyramid.httpexceptions import HTTPNotFound

from pyramid.view import view_config
from pyramid.response import Response, FileResponse
from simpleconfigparser import simpleconfigparser

from aof.tools.AppPool import AppPool
from aof.tools import deploy, o, ae_tools

from aof.static.data.static_data import META
from aof.static.data.static_data import SITE_MENU

config = simpleconfigparser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir)+'/aof.conf')

app_pool = config.Paths.app_ensemble_location

log = logging.getLogger(__name__)

@view_config(route_name='home', renderer='templates/home.mako')
def home_view(request):

    return {'menu': SITE_MENU,
            'meta': META,
            'page_title': 'Home'}

class AppPoolViews():

    def __init__(self, request):
        self.request = request

    @view_config(route_name='app-pool', renderer='templates/app-pool.mako')
    def ap_show_view(self):
        return {'menu': SITE_MENU,
                'meta': META,
                'page_title': 'App-Pool',
        }

    @view_config(route_name='api', match_param='tool=get_app_pool', renderer='json')
    def ap_get_app_pool_json(self):
        ap = AppPool.Instance("http://localhost:8081/static/App-Pool/pool.ttl")
        query = """
        PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
        SELECT DISTINCT *
        WHERE {
        ?uri rdfs:label ?name ;
            adl:currentBinary ?binary .

        OPTIONAL {
        ?uri adl:hasIntent [
            adl:intentString ?intent_string ;
            adl:intentPurpose ?intent_purpose
            ] .
        }

        }
        """
        res = ap.query(query)
        json = res.serialize(format="json").decode()

        log.info(json)
        return {'json': json}

class AppEnsembleViews():
    ae_dict = None

    def __init__(self, request):
        self.request = request
        if not type(self).ae_dict:
            type(self).ae_dict = ae_tools.getExistingAE()

    @view_config(route_name='deploy', renderer='templates/deploy.mako')
    def deploy_view(request):
        return {'menu': SITE_MENU,
                'meta': META,
                'page_title': 'Deploy'}

    @view_config(route_name='api', match_param='tool=get_ae_info', renderer='json')
    def ae_get_ae_info_json_view(self):
        ae_info = dict()
        for key, ae in self.ae_dict.items():
            apps = ae_tools.getRequiredApps(ae).serialize(format='json').decode()
            id = key
            path = ae.ae_pkg_path
            ae_info[key] = {'id': id, 'path': path, 'apps': apps}

        return {'json': ae_info}

    @view_config(route_name='api', match_param='tool=get_ae_pkg')
    def ae_get_ae_pkg_view(self):
        param = self.request.params.getone('ae_id')
        if param in self.ae_dict:
            ae = self.ae_dict.get(param)
            response = FileResponse(
                ae.ae_pkg_path,
                request=self.request,
                content_type='application/vnd.aof.package-archive'
                )
            response.content_disposition = 'attachement; filename="'+param+".ae"
        else:
            response = HTTPNotFound('There is no such resource')
        return response


@view_config(route_name='orchestrate', renderer='templates/orchestrate.mako')
def o_view(request):
    return {'menu': SITE_MENU,
            'meta': META,
            'page_title': 'Orchestrate'
    }

@view_config(name='o_select.json', renderer='json')
def o_select_view_json(request):
    select = o.FolderName(models_path)
    folderNames = select.getFolderNames()
#    print(folderNames)
    return {'select':folderNames}

@view_config(name='o_get_apps.json', renderer='json')
def o_get_apps_view_json(request):
    modelName = request.params.get('data')
    global orchestration
    orchestration = o.Orchestration(modelName, models_path)
    requestApps = orchestration.getRequestApps()
    availableApps = orchestration.getAvailableApps()
# use global to the orchestration
    return {'requestApps': requestApps, 'availableApps': availableApps}

@view_config(name='o_orchestration.json', renderer='json')
def o_orchestration_view_json(request):
    request_selected_apps = request.params.get('request_selected_apps')
    availabel_apps = request.params.get('available_apps')
    modelName = request.params.get('modelName')
    orchestration = o.Orchestration(modelName, models_path, request_selected_apps, availabel_apps)
    result = orchestration.createAppEnsemble()
    print(result)
    test = "{ae_result:[{name:'" + result + "'}]}"
    result_1 = "haha";
    test_1 = "{ae_result:[{name:'" + result_1 + "'}]}"
    print(test)
    print(test_1)
    return {'ae_result': test}

@view_config(route_name='demo', renderer='templates/demo.mako')
def dp_1_view(request):
    device = deploy.Device()
    has = device.getStatus()
    return {'hasDevice': has, 'menu': SITE_MENU, 'meta': META, 'page_title': 'Demo'}

@view_config(route_name='demo_tool', match_param="tool=demo_tool", renderer='templates/demo_tool.mako')
def dp_2_view(request):
    return {'menu': SITE_MENU, 'meta': META, 'page_title': 'Demo_tool'}

@view_config(name='demo_apps.json', renderer='json')
def demo_apps_view_json(request):
    situation = request.params.get('demo')
    if situation == None:
        ae_location_full = ''
        print(folderNameDeploy)
        if folderNameDeploy.endswith('.ttl'):
            ae_location = folderNameDeploy.replace('.ttl','').title() + '/' + folderNameDeploy
            ae_location_full = os.path.join(app_ensemble_deploy_location, ae_location)
        else:
            ae_location = folderNameDeploy + '/' + folderNameDeploy.lower() + '.ttl'
            ae_location_full = os.path.join(app_ensemble_deploy_location, ae_location)
        dp = deploy.Deploy(ae_location_full)
        apps = dp.getapps()
        return {'apps':apps}
    else:
        demo = deploy.Deploy(app_ensemble_location)
        apps = demo.getapps()
        return {'apps':apps}

@view_config(name='demo_install.json', renderer='json')
def demo_install_view_json(request):
    name = request.params.get('data')
    install = deploy.Install(name)
    result = install.getStatus()
    return {'result':result}

@view_config(route_name='info', renderer='templates/info.mako')
def info_view(request):
    return {'menu': SITE_MENU,
            'meta': META,
            'page_title': 'Info'}
import os

from pyramid.view import view_config
from pyramid.response import Response
from simpleconfigparser import simpleconfigparser

from aof.tools import app_pool
from aof.tools import deploy
from aof.tools import o

from aof.static.data.static_data import META
from aof.static.data.static_data import SITE_MENU

config = simpleconfigparser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir)+'/aof.conf')

app_ensemble_location = config.Paths.app_ensemble_location
models_path = config.Paths.models_path

@view_config(route_name='home', renderer='templates/home.mako')
def home_view(request):

    return {'menu': SITE_MENU,
            'meta': META,
            'page_title': 'Home'}

@view_config(route_name='app-pool', renderer='templates/app-pool.mako')
def ap_show_view(request):
    json = listAP()
    print(json)
    return {'menu': SITE_MENU,
            'meta': META,
            'page_title': 'App-Pool',
            'json': json
    }

@view_config(route_name='orchestrate', renderer='templates/orchestrate.mako')
def o_view(request):
    return {'menu': SITE_MENU,
            'meta': META,
            'page_title': 'Orchestrate'
    }

@view_config(name='o_select.json', renderer='json')
def o_select_view(request):
    configfiles = "{select:[{name:'configfile_1'},{name:'configfile_2'}]}"
    select = o.FolderName(models_path)
    folderNames = select.getFolderNames()
#    print(folderNames)
    return {'select':folderNames}

@view_config(name='o_get_apps.json', renderer='json')
def o_get_apps_view(request):
    modelName = request.params.get('data')
    apps = o.Orchestration(modelName, models_path)
    requestApps = apps.getRequestApps()
    availableApps = apps.getAvailableApps()
    print(requestApps)
    print(availableApps)
    return {'requestApps': requestApps, 'availableApps': availableApps}

@view_config(route_name='deploy', renderer='templates/deploy.mako')
def deploy_view(request):
    return {'menu': SITE_MENU,
            'meta': META,
            'page_title': 'Deploy'
    }

@view_config(route_name='demo', renderer='templates/demo.mako')
def dp_1_view(request):
    device = deploy.Device()
    has = device.getStatus()
    return {'hasDevice': has, 'menu': SITE_MENU, 'meta': META, 'page_title': 'Demo'}

@view_config(route_name='demo_tool', match_param="tool=demo_tool", renderer='templates/demo_tool.mako')
def dp_2_view(request):
    return {'menu': SITE_MENU, 'meta': META, 'page_title': 'Demo_tool'}

@view_config(name='demo_apps.json', renderer='json')
def demo_apps_view(request):
    demo = deploy.Deploy(app_ensemble_location)
    apps = demo.getapps()
    return {'apps':apps}

@view_config(name='demo_install.json', renderer='json')
def demo_install_view(request):
    name = request.params.get('data')
    install = deploy.Install(name)
    result = install.getStatus()
    return {'result':result}

def listAP():
    query = """
    PREFIX ap: <http://eatld.et.tu-dresden.de/ap/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?app_uri ?label ?apk_uri
    WHERE {
	?app_uri a ap:App .
	?app_uri rdfs:label ?label .
	OPTIONAL {
		?app_uri ap:availableAt ?apk_uri .
	}
    } 
    LIMIT 100
    """
    ap = app_pool.LocalAppPool()
    json = ap.queryAP(query)
    return json
import os

from pyramid.view import view_config
from pyramid.response import Response
from simpleconfigparser import simpleconfigparser

from aof.tools import app_pool
from aof.tools import deploy

from aof.static.data.static_data import META
from aof.static.data.static_data import SITE_MENU

config = simpleconfigparser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir)+'/aof.conf')

app_ensemble_location = config.Paths.app_ensemble_location

menu = SITE_MENU
project = META['appname']

@view_config(route_name='home', renderer='templates/home.mako')
def home_view(request):

    return {'menu': menu,
            'project': project,
            'page_title': 'Home'}

@view_config(route_name='app-pool', renderer='templates/ap_show.pt')
def ap_show_view(request):
    json = listAP()
    print(json)
    return {'menu': menu,
            'project': project,
            'page_title': 'App-Pool',
            'json': json
    }

@view_config(route_name='orchestrate', renderer='templates/orchestrate.mako')
def o_view(request):
    return {'menu': menu,
            'project': project,
            'page_title': 'Orchestrate'
    }

@view_config(route_name='deploy', renderer='templates/deploy.mako')
def deploy_view(request):
    return {'menu': menu,
            'project': project,
            'page_title': 'Deploy'
    }

@view_config(route_name='demo', renderer='templates/demo.mako')
def dp_1_view(request):
    device = deploy.Device()
    has = device.getStatus()
    return {'hasDevice': has, 'menu': menu, 'project': project}

@view_config(route_name='demo_tool', match_param="tool=demo_tool", renderer='templates/demo_tool.mako')
def dp_2_view(request):
    return {'project': 'Deploy'}

@view_config(name='demo_json.json', renderer='json')
def dp_json_view(request):
    print(app_ensemble_location)
    dp = deploy.Deploy(app_ensemble_location)
#    dp_json = dp.getJSON()
#    return {'result':dp_json}

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
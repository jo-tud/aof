from pyramid.view import view_config
from pyramid.response import Response
from aof.app_pool import app_pool
from aof.deploy import deploy
import os
import sys
from simpleconfigparser import simpleconfigparser

config = simpleconfigparser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir)+'/aof.conf')

app_ensemble_location = config.Paths.app_ensemble_location

@view_config(route_name='home', renderer='templates/dash.pt')
def my_view(request):
    return {'project': 'AOF'}

@view_config(route_name='ap_tools', match_param="tool=show", renderer='templates/ap_show.pt')
def ap_show(request):
    json = listAP()
    print(json)
    return {'project': 'App-Pool: show', 'json': json}
  
@view_config(route_name='ap_tools', renderer='templates/ap_all.pt')
def ap_all(request):
    return {'project': 'App-Pool: catch all'}

@view_config(route_name='o_tools', renderer='templates/orchestration.pt')
def o(request):
    return Response('Here the orchestration tools will go. Tool called: %(tool)s!' % request.matchdict)

@view_config(route_name='dp_tools', renderer='templates/dp_1.pt')
def dp_1(request):
    device = deploy.Device()
    has = device.getStatus()
    return {'hasDevice': has}

@view_config(route_name='dp_tools', match_param="tool=deploy_2", renderer='templates/dp_2.pt')
def dp_2(request):
    return {'project': 'Deploy'}

@view_config(route_name='dp_json', renderer='json')
def dp_json(request):
    dp = deploy.Deploy(app_ensemble_location)
    dp_json = dp.getJSON()
    return {'result':dp_json}

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
    ap = app_pool.LocalAppPool(query)
    json = ap.queryAP()
    return json
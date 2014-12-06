#! /usr/bin/python3
# -*- coding: utf8 -*-
'''
o -- Implementation of the Orchestration Process

@author:     Johannes Pfeffer
        
@version:    0.5

@release:    elephant

'''

import os # os abstraction (e.g. listdir)
from rdflib import Graph, ConjunctiveGraph, URIRef, Namespace, RDF, RDFS, BNode, Literal
from rdflib.plugins.memory import IOMemory
import time # local time for App Ensemble name

from simpleconfigparser import simpleconfigparser

# Adapter
from aof.tools.univie_adapter import CV_BPM

from rdflib import Literal

###########################################
# Globals
###########################################

CONFIG_FILE = 0
PLACEHOLDER_APP = URIRef("http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#SkeletonApp_G0M8iQlfoOQQ")

class FolderName:
    def __init__(self, folder_path):
        list = os.listdir(folder_path)
        jsonString = '{select:['
        for i in range(0, len(list)-1):
            if list[i] != 'README':
                jsonString =  jsonString + add(list[i])
        jsonString = jsonString + endadd(list[len(list)-1]) + ']}'
        self.jsonString = jsonString

    def getFolderNames(self):
#        print(self.jsonString)
        return self.jsonString

# Definition of general namespaces
NS_XML = Namespace("http://www.w3.org/XML/1998/namespace")
NS_RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
NS_RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

# Definition of orchestration specific namespaces
NS_O = Namespace("http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#")

# Make prefix dictionary
ns=dict(xml=NS_XML,rdf=NS_RDF,rdfs=NS_RDFS,o=NS_O)

SILENT = True

class Orchestration:
    def __init__(self, modelName, models_path,request_selected_apps=None, available_apps=None):
        # reade the file of configure

        if request_selected_apps != None:
            self.request_selected_apps = request_selected_apps

        if available_apps != None:
            self.available_apps = available_apps

        config_file = models_path + modelName + '/' + modelName.lower() + '.conf'
        print("Reading configuration from file " + config_file + "\n")
        config = simpleconfigparser()
        config.read([config_file])

        if config.General.ae_name :
            ae_name = config.General.ae_name
            ae_name = ae_name.replace(" ", "_")
        if config.Paths.ap_folder :
            ap_folder = config.Paths.ap_folder
        if config.Paths.output_folder:
            output_folder = config.Paths.output_folder
        if (config.Paths.supplements_file):
            supplements_file = config.Paths.supplements_file
        if config.univie_adapter.univie_model_file:
            univie_model_file = config.univie_adapter.univie_model_file

        ###########################################
        # Preparations
        ###########################################

        # Graph for the combined model
        store = IOMemory()
        g = ConjunctiveGraph(store=store)

        for prefix in ns:
            g.bind(prefix,ns.get(prefix))

        # Create an empty model for the App Ensemble
        o_id = ae_name+"_"+timestring()
        o = Graph(store=store, identifier=o_id)

        # Prepare the orchestration model
        prepareModel(g,o_id)

        # use configuration if available
        if config.univie_adapter.univie_model_file:
            cvbpm = CV_BPM(model_file=univie_model_file, SILENT=SILENT)
        else:
            cvbpm = CV_BPM(SILENT=SILENT)

        # Add apps
        o += cvbpm.getApps().graph

        # Add entry point
        addEntryPoint(g,o_id,o_id,cvbpm.getEntryPoint())

        # Add supplemented triples
        if (supplements_file is not None):
            supplements = Graph(store=store,identifier="supplements")
            supplements.parse(supplements_file,format="turtle")
            o += supplements

        self.o = o
        self.app_pool = APP_POOL(o, store, ap_folder)

    def getRequestApps(self):
        return self.app_pool.requestApps

    def getAvailableApps(self):
        return self.app_pool.availableApps

    def createAppEnsemble(self):
        create(self.o, self.app_pool.ap, self.request_selected_apps, self.available_apps)

def create(o, ap, request_selected_apps, available_apps):
    request_selected_apps_list = request_selected_apps.split(',')
    available_apps_list = available_apps.split(',')
    results = list()
    for i in range(0, len(request_selected_apps_list)):
        request = request_selected_apps_list[i].split('§§')[0]
        selected = request_selected_apps_list[i].split('§§')[1]
        test1 = o.value(None, NS_O.Name, Literal(request))
        test2 = ap.value(None, RDFS.label, Literal(selected))
        print(test1)
        print(test2)

class APP_POOL:
    def __init__(self, o, store, ap_folder):
        ###########################################
        # Select
        ###########################################

        '''
        Since there is no real selection yet, we load a supplement model that connects the Apps to Generic Apps from the App Pool
        '''

        # Load the App Pool descriptions
        ap = Graph(store=store,identifier="ap")
        for appPoolDescrFile in os.listdir(ap_folder):
            if appPoolDescrFile.endswith(".ttl"):
                # print(appPoolDescrFile)
                ap.parse(os.path.join(ap_folder,appPoolDescrFile), format = "turtle")

        # Load app descriptions
        for appDescrFile in ap.objects(None,NS_O.descriptionFilename):
            if appDescrFile.endswith(".ttl"):
                ap.parse(ap_folder + "apps/"+appDescrFile, format = "turtle")

        # Honor existing selections
        appRequests = list()
        appRequestTriples = list()
        for req in o.subjects(RDF.type, NS_O.AppRequest):
            preselection = o.value(req, NS_O.instanceOf, None)
            if (preselection is None):
                appRequestTriples.append(( req, NS_O.instanceOf, PLACEHOLDER_APP))
            else:
                appRequestTriples.append(( req, NS_O.instanceOf, preselection))
            appRequests.append(req)
        self.requestApps = getRequestApps(appRequestTriples, o, ap)
        self.availableApps = getAvailableApps(ap)
        self.ap = ap

def timestring():
    timestring = time.strftime("%Y-%m-%d_%Hh%Mm%Ss",time.localtime())
    return timestring

def prepareModel(graph,ctx_id):
    # Create the nodes that are required for an orchestration model
    qstr= """
    WITH <%s>
    INSERT {
        _:Orchestration a o:Orchestration ;
            o:hasAppEnsemble _:AppEnsemble .

        _:AppEnsemble a o:AppEnsemble ;
            o:Name "%s" ;

            # Set the Intent that will be used for placeholder apps
            o:hasDefaultIntent "eu.comvantage.iaf.SIMPLE_MESSAGE" ;

            # Always require the following apps
            o:requiresApp o:IAFManagementComponent_ZIRiErVxZHc- ;
            o:requiresApp o:TUDSimpleMessage_MBrh2UmSe3AP ;
            o:requiresApp o:TUDSimpleList_NryuJDGzjNXl ;
            o:requiresApp o:OIFileManager_uNSUZ7-rb3mm ;
            o:requiresApp o:IAFLogin_Zvy4kvB-fH9T .

    }
    WHERE {}
    """ % (ctx_id, ctx_id)

    graph.update(qstr, initNs=ns)

def addEntryPoint(graph,ctx_id,ae,entrypoint):
    # Add an entry point "entrypoint" to App Ensemble "ae" with context "ctx_id" in graph "graph"
    qstr= """
    WITH <%s>
    INSERT {
        ?appensemble o:hasEntryPoint <%s> .
    }
    WHERE {
        ?appensemble o:Name "%s" .
        }
    """ % (ctx_id, entrypoint, ae)
    # print(qstr)

    graph.update(qstr, initNs=ns)

def getAppLabel(app, graph):
    return graph.value(app, RDFS.label, None)

def getAppName(app, graph):
    return graph.value(app, NS_O.Name, None)

def getRequestApps(appRequestTriples, graph_o, graph_ap):
    appRequsts = list()
    for (s,p,o) in appRequestTriples:
        app_dict = dict()
        request_app = getAppName(s, graph_o).toPython()
        preselcection_app = getAppLabel(o, graph_ap)
        if preselcection_app == None:
            preselcection_app = "No"
        else:
            preselcection_app = preselcection_app.toPython()

        app_dict[request_app] = preselcection_app
        appRequsts.append(app_dict)

    jsonString = '{request_apps:['
    for i in range(0, len(appRequsts)-1):
        for k in appRequsts[i]:
            jsonString =  jsonString + add2(k,appRequsts[i][k])

    for k in appRequsts[(len(appRequsts)-1)]:
        jsonString = jsonString + lastadd2(k,appRequsts[(len(appRequsts)-1)][k]) + ']}'

    return jsonString

def getAvailableApps(graph_ap):
    available_apps = list()
    for app in graph_ap.subjects(RDF.type,NS_O.GenericApp):
        available_apps.append(getAppLabel(app, graph_ap).toPython())
    jsonString = '{available_apps:['
    for i in range(0, len(available_apps)-1):
        jsonString =  jsonString + add(available_apps[i])
    jsonString = jsonString + endadd(available_apps[len(available_apps)-1]) + ']}'
#    print(jsonString)
    return jsonString

def add(name):
    item = '{name:' + "'" + name + "'"  + '},'
    return item

def endadd(name):
    item = '{name:' + "'" + name + "'"  + '}'
    return item

def add2(reqeust,preselection):
        item = '{name:' + "'" + reqeust + "'" + ',' + 'preselection:' + "'" + preselection + "'" + '},'
        return item

def lastadd2(request,preselection):
        item = '{name:' + "'" + request + "'" + ',' + 'preselection:' + "'" + preselection + "'" + '}'
        return item
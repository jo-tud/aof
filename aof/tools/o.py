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

from aof.tools.o_errors import CardinalityError, CLIError

import shutil

###########################################
# Globals
###########################################

CONFIG_FILE = 0
CREATE_SUPPLEMENTFILE = 0
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
        self.ap_folder = ap_folder
        self.app_pool = APP_POOL(o, store, ap_folder)
        self.cvbpm = cvbpm
        self.output_folder = output_folder
        self.o_id = o_id


    def getRequestApps(self):
        return self.app_pool.requestApps

    def getAvailableApps(self):
        return self.app_pool.availableApps

    def createAppEnsemble(self):
        return create(self.o, self.app_pool.ap, self.request_selected_apps, self.available_apps, self.ap_folder, self.cvbpm,
               self.output_folder, self.o_id)

def create(o, ap, request_selected_apps, available_apps, ap_folder, cvbpm, output_folder, o_id):
    request_selected_apps_list = request_selected_apps.split(',')
    available_apps_list = available_apps.split(',')
    results = list()
    for i in range(0, len(request_selected_apps_list)):
        request = request_selected_apps_list[i].split('§§')[0]
        selected = request_selected_apps_list[i].split('§§')[1]
        if any(selected in s for s in available_apps_list):
            triple = (URIRef(o.value(None, NS_O.Name, Literal(request))), NS_O.instanceOf, ap.value(None, RDFS.label, Literal(selected)))
            results.append(triple)
        else:
            triple = (URIRef(o.value(None, NS_O.Name, Literal(request))), NS_O.instanceOf, PLACEHOLDER_APP)
            results.append(triple)
#    print(results)

    # clean old selections (they are added again in next step)
    for old in o.triples((None,NS_O.instanceOf,None)):
        o.remove(old)

    # add selection
    for app in results:
        o.add(app)
        o.add((app[0], RDF.type, NS_O.SelectedApp))

    # Final sanity checks
    # Note: max cardinality of NS_O:instanceOf is 1
    for req in o.subjects(RDF.type, NS_O.AppRequest):
        cardinality = len(list(o.objects(req,NS_O.instanceOf)))
        #print(cardinality)
        if (cardinality != 1):
            raise CardinalityError(1,cardinality,"Exactly one app must be selected for each app request "+req)

    # print selection result
    indent = max([len(getAppName(row[0], o)) for row in results])
    for sub,pre,obj in o.triples((None,NS_O.instanceOf,None)):
        print(getAppName(sub, o).rjust(indent)+" -> "+getAppLabel(obj, ap));

    ## Make set of Apps to copy
    appsToCopy = set()

    # Add app descriptions for selected apps to orchestration model
    #ToDo: Find a more elegant way to do this. It should be possible to add a transitive subgraph from ap
    for selectedApp in o.objects(None,NS_O.instanceOf):
        appDescrFile = ap.value(selectedApp, NS_O.descriptionFilename, None, "", False)
        filename = ap.value(selectedApp, NS_O.filename, None, "", False)
        if appDescrFile != "" :
            o.parse(ap_folder + "apps/"+appDescrFile, format = "turtle")
        if filename != "":
            appsToCopy.add(str(filename))

    # Add app descriptions for required apps to orchestration model
    for requiredApp in o.objects(None,NS_O.requiresApp):
        appDescrFile = ap.value(requiredApp, NS_O.descriptionFilename, None, "", False)
        filename = ap.value(requiredApp, NS_O.filename, None, "", False)
        if appDescrFile != "" :
            o.parse(ap_folder + "apps/"+appDescrFile, format = "turtle")
        if filename != "" :
                appsToCopy.add(str(filename))

#    print(appsToCopy)
    ###########################################
    # Adapt
    ###########################################

    # Currently do nothing

    ###########################################
    # Manage
    ###########################################

    # Add succession types (XOR, OR, AND)
    for app in o.subjects(RDF.type, NS_O.App):
        sucType = cvbpm.getSuccessionType(app)
        o.add( (app, NS_O.hasSuccessionType, sucType))

    ###########################################
    # Write the App-Ensemble to filesystem
    ###########################################

    # Set App Ensemble Folder
    ae_folder = os.path.join(output_folder,o_id)

    # Create directories
    os.mkdir(ae_folder)
    os.mkdir(os.path.join(ae_folder,"apps",""))

    if CREATE_SUPPLEMENTFILE == 1:
        createSupplementsFile(results,ae_folder)

    # Copy apps from pool
    for filename in appsToCopy:
        shutil.copyfile(os.path.join(ap_folder,"apps",filename), os.path.join(ae_folder,"apps",filename))

    # Serialize orchestration model
    aeFile = open(os.path.join(ae_folder,o_id+".ttl"),'wb')
    aeFile.write(o.serialize(format="turtle"))
    aeFile.close()

    finish = "\nApp Ensemble was created in " + ae_folder
    return finish





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

def createSupplementsFile(selectedApps, ae_folder):
    # Serialize supplements file
    supp = ""
    for app in selectedApps:
        supp += app[0].n3() + " " +app[1].n3()+ " " +app[2].n3()+ " .\n"
    # print(supp)
    suppFile = open(os.path.join(ae_folder,"supplements.ttl"),'w')
    suppFile.write(supp)
    suppFile.close()
    print("\nCreated supplements.ttl file")
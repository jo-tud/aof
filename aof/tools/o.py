#! /usr/bin/python3
# -*- coding: utf8 -*-
'''
o -- Implementation of the Orchestration Process

@author:     Johannes Pfeffer
        
@version:    0.5

@release:    elephant

'''

from rdflib import Graph, ConjunctiveGraph, URIRef, Namespace, RDF, RDFS, BNode, Literal
from rdflib.plugins.memory import IOMemory
from operator import methodcaller

import os # os abstraction (e.g. listdir)

import sys # e.g. for exit()

import time # local time for App Ensemble name
import shutil # for filesystem operations

from argparse import ArgumentParser # for command line arguments
from simpleconfigparser import simpleconfigparser

# GUI related
from tkinter import *
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import ttk, messagebox

# Adapter
from univie_adapter import CV_BPM

# Errors
from o_errors import CardinalityError, CLIError
from lib2to3.pgen2.tokenize import Triple
from operator import itemgetter
from _ast import operator

###########################################      
# Globals
########################################### 

CONFIG_FILE = 0
PLACEHOLDER_APP = URIRef("http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#SkeletonApp_G0M8iQlfoOQQ")

###########################################      
# Command line arguments
###########################################   

parser = ArgumentParser(description="Select Step", add_help=True, )

# name
parser.add_argument("-n", "--name", dest="name",
    help="Set the name of the produced App-Ensemble, will be used in the folder and filename", metavar="NAME") 

# base - should change the base of all paths givent from ./ to something else. Todo.
# parser.add_argument("--base", dest="base",
#    help="Change the base for all paths", metavar="BASE")

#  configuration file
parser.add_argument("-c", "--conf_file", dest="conf_file", 
    help="Specify orchestration config file", metavar="FILE")

#  supplements file
parser.add_argument("--supplements_file", dest="supplements_file", 
    help="Specify file with supplemented triples that will be added to the orchestration model", metavar="FILE")

# simulated mode 
parser.add_argument("--simulate", dest="simulate",
    help="Simulate the orchestration process. Don't perform any actual file operations such as creating directories or copying files", action='store_true')

# silent mode
parser.add_argument("-i", "--interactive", dest="interactive",
        help="Be more interactive. E.g. give choices what graph to load, etc... Try this if the automatic mode produces errors.", action='store_true') 

# create supplements file
parser.add_argument("--create-supplements-file", dest="create_supplements",
        help="This option will create a supplements file for the app selection of the generated App Ensemble. This file can be used in subsequent orchestrations to automate the process.", action='store_true') 

args, remaining_argv = parser.parse_known_args()

    
## Configuration

# set the SILENT variable
if args.interactive == True:
    SILENT = False
else:
    SILENT = True

# set the SIMULATE variable
if args.simulate == True:
    SIMULATE = True
    print("\nSIMULATION ON! No file operations will be performed")
else:
    SIMULATE = False
    
if args.supplements_file:
    supplements_file = os.path.abspath(args.supplements_file)
else:
    supplements_file = None
    
if args.name:
    ae_name = args.name
    ae_name = ae_name.replace(" ", "_")
else:
    ae_name = "AE"

print("\n")
if args.conf_file:
    
    CONFIG_FILE = 1
    
    print("Reading configuration from file " + args.conf_file + "\n")
    config = simpleconfigparser()
    config.read([args.conf_file])
    
    if config.General.ae_name :
        ae_name = config.General.ae_name
        ae_name = ae_name.replace(" ", "_")
    if config.Paths.ap_folder :
        ap_folder = config.Paths.ap_folder
    if config.Paths.output_folder:
        output_folder = config.Paths.output_folder
    if (config.Paths.supplements_file and supplements_file is None):
        supplements_file = config.Paths.supplements_file
    
    if config.univie_adapter.univie_model_file:
        univie_model_file = config.univie_adapter.univie_model_file
    
else:
    
    CONFIG_FILE = 0
    
    master = Tk()
    ap_folder = askdirectory(title="Select the App-Pool folder") + "/"
    output_folder = askdirectory(title="Choose the output folder for the App-Ensemble") + "/" 
    master.quit()
    master.destroy()

# Print main configuration

print("App-Ensemble name: " + str(ae_name))
print("App-Pool folder: " + str(ap_folder))
print("Output folder: " + str(output_folder))
print("Supplements file: " + str(supplements_file))


def getAppName(app):
    return g.value(app, NS_O.Name, None)

def getAppLabel(app):
    return g.value(app, RDFS.label, None)

def selectApps(appRequestTriples):
    optionMenus = list()
    appRequests = list()
    preselection = list()
    
    appRequestTriples.sort()
                               
    for (s,p,o) in appRequestTriples:
        appRequests.append(s)
        preselection.append(getAppLabel(o))
    
    def done():
            root.quit()
    
    def windowclosehandler():
        done()
    
    # get the available apps from the pool
    available_apps = dict()
    r=0
    temp = list();
    for app in ap.subjects(RDF.type,NS_O.GenericApp):
        available_apps[getAppLabel(app)] = app
        r+=1
    
    sorted_available_apps = sorted(available_apps)
    sorted_available_apps.insert ( 0 , ' ' )

    root = Tk()
    root.title("Manual App Selection Module")
    root.protocol("WM_DELETE_WINDOW", windowclosehandler)
    
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    
    selectedApps = list()
    
    # Build selection table
    r=0
    for req in appRequests:
        ttk.Label(mainframe, text=getAppName(req), relief=FLAT).grid(row=r,column=0,sticky=W)
        ttk.Label(mainframe, text="->", relief=FLAT).grid(row=r,column=1,sticky=(W))
        
        selectedApps.append(StringVar())
        optionMenus.append(ttk.OptionMenu(mainframe,selectedApps[r], *sorted_available_apps).grid(row=r, column=2,sticky=(EW)))
        selectedApps[r].set(preselection[r])
        r+=1
    
    ttk.Button(mainframe, text="Done", command=done).grid(column=0, columnspan=3, row=r+1, sticky=E)
    
    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
    
    root.mainloop()
    
    results = list()
    for i, app in enumerate(selectedApps):
        triple = (URIRef(appRequests[i]),NS_O.instanceOf,URIRef(available_apps.get(Literal(app.get()),PLACEHOLDER_APP)) ) 
        results.append( triple )
        #print(triple)
    return results

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
    
def serializeModel(format="turtle"):
    print(g.serialize(format="%s" % format).decode())
    
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
    
if __name__ == "__main__":
    
    ###########################################      
    # Preparations
    ###########################################
    
    # Definition of general namespaces

    NS_XML = Namespace("http://www.w3.org/XML/1998/namespace")
    NS_RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    NS_RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    
    # Definition of orchestration specific namespaces
    NS_O = Namespace("http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#")
    
    # Make prefix dictionary
    ns=dict(xml=NS_XML,rdf=NS_RDF,rdfs=NS_RDFS,o=NS_O)
        
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
    
    # Create an instance of the adapter object
    
    # use configuration if available
    if CONFIG_FILE and config.univie_adapter.univie_model_file:
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
            
    
    # Initial sanity checks
    # Note: max cardinality of NS_O:instanceOf is 1
    for req in o.subjects(RDF.type, NS_O.AppRequest):
        cardinality = len(list(o.objects(req,NS_O.instanceOf)))
        if (cardinality not in [0,1]):
            raise CardinalityError(1,cardinality,"Exactly one app must be selected for each app request "+req)
        
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
    # print(appRequestTriples)
    
    print("### SELECT ###")
    # do the selection
    selectedApps = selectApps(appRequestTriples)
    
    # clean old selections (they are added again in next step)
    for old in o.triples((None,NS_O.instanceOf,None)):
        o.remove(old)

    # add selection
    for app in selectedApps:
        o.add(app)
        o.add((app[0], RDF.type, NS_O.SelectedApp))
    
    # Final sanity checks
    # Note: max cardinality of NS_O:instanceOf is 1
    for req in o.subjects(RDF.type, NS_O.AppRequest):
        cardinality = len(list(o.objects(req,NS_O.instanceOf)))
        # print(cardinality)
        if (cardinality != 1):
            raise CardinalityError(1,cardinality,"Exactly one app must be selected for each app request "+req)
        
    # print selection result
    indent = max([len(getAppName(row[0])) for row in selectedApps])
    for sub,pre,obj in o.triples((None,NS_O.instanceOf,None)):
        print(getAppName(sub).rjust(indent)+" -> "+getAppLabel(obj));
    
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
    
    if not SIMULATE :
        
        # Set App Ensemble Folder
        ae_folder = os.path.join(output_folder,o_id)
        
        # Create directories
        os.mkdir(ae_folder)
        os.mkdir(os.path.join(ae_folder,"apps",""))
        
        # create supplements file
        if args.create_supplements:
            createSupplementsFile(selectedApps,ae_folder)
        
        # Copy apps from pool
        for filename in appsToCopy:
            shutil.copyfile(os.path.join(ap_folder,"apps",filename), os.path.join(ae_folder,"apps",filename))
        
        # Serialize orchestration model
        aeFile = open(os.path.join(ae_folder,o_id+".ttl"),'wb')
        aeFile.write(o.serialize(format="turtle"))
        aeFile.close()
        
        print("\nApp Ensemble was created in " + ae_folder)
    else: 
        print("\nSIMULATION ON! No file operations were performed")
    
    sys.exit()


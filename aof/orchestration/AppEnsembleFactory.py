__author__ = 'Korbi'
from xml.dom.minidom import parseString, NodeList
from rdflib import ConjunctiveGraph, URIRef, BNode, Literal, RDF, RDFS, Namespace
from rdflib.plugins.memory import IOMemory
from zipfile import ZipFile
import time
from urllib.request import urlretrieve
from urllib.error import URLError
from aof.views.AppPoolViews import fill_graph_by_subject
import logging,os
from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool
from pyramid.response import Response
from pyramid.threadlocal import get_current_registry

AOF = Namespace('http://eatld.et.tu-dresden.de/aof/')
BPMN2 = Namespace('http://dkm.fbk.eu/index.php/BPMN2_Ontology#')
ORCHESTRATION = Namespace('http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#')

class OrchestrationFactory():
    def __init__(self, bpmnxml):
        self.bpmn = bpmnxml
        self.dom = parseString(bpmnxml)
        self.appEnsembles = {}
        self._extractAppEnsembles()

    def _extractAppEnsembles(self):
        participants = self.dom.getElementsByTagName('bpmn2:participant')
        for p in participants:
            if (p.getAttribute('aof:isAppEnsemble')):
                try:
                    self.appEnsembles[p.getAttribute('id')] = {}
                    self.appEnsembles[p.getAttribute('id')]["participantName"] = p.getAttribute('name').replace(" ","-")
                    name=p.getAttribute('processRef')
                    self.appEnsembles[p.getAttribute('id')]["name"] = name
                    self.appEnsembles[p.getAttribute('id')]["tmp_path"]=AssetResolver().resolve('aof:tmp/ae-trash/'+name).abspath()
                except:
                    pass
        processes = self.dom.getElementsByTagName('bpmn2:process')
        for p in processes:
            id = p.attributes['id'].nodeValue
            for ae in self.appEnsembles:
                if self.appEnsembles[ae]["name"] == id:
                    self.appEnsembles[ae]["dom"] = p

    def _saveBpmn(self,path):
        try:
            file = open(path+".bpmn", 'wb')
            file.write(bytes(self.bpmn,"utf-8"))
            file.close()
        except:
            # TODO
            pass

    def create(self):
        text=""
        status=0
        resp=Response("Orchestration sucessfully created!","201 Created")
        for ae in self.appEnsembles:
            self._saveBpmn(self.appEnsembles[ae]["tmp_path"])
            response=AppEnsembleFactory(self.appEnsembles[ae]).create()
            text+=response.response+"\n"
            status +=response.status

        if(status==0):
            return Response("Orchestration sucessfully created!","201 Created")
        if (status<=len(self.appEnsembles)):
            return Response("Orchestration sucessfully created!"+text,"201 Created")
        else:
            return Response(text,"500 Internal Server Error")



class AppEnsembleFactory():
    def __init__(self,ae):
        #self.participantName=ae["participantName"]
        self.name=ae["name"]
        self.dom=ae["dom"]
        self.required_apps = []
        self.warnings = {}
        self.log = [];
        self.tmp_path =ae["tmp_path"]   # tmp-path for all ae-files

        self._extractRequiredApps()

    def registerWarning(self, part, message):
        self.warnings[part] = message

    def returnWarnings(self):
        resp=""
        if len(self.warnings) > 0:
            resp += "<br><br><strong>Warnings:</strong><ul>"
            for w in self.warnings:
                resp += "<li>" + self.warnings[w] + "</li>"
            resp += "</ul>Please watch the Logfile stored in the AppEnsemble!"
        return resp

    def registerLogEntry(self, message):
        self.log.append({'time':time.strftime('%Y-%m-%d %H:%M:%S'),'msg':message})

    # TODO
    def saveLog(self,destination):
        logfile = open(destination, 'w')

    def _extractRequiredApps(self):
        for e in self.dom.getElementsByTagName('bpmn2:userTask'):
            if e.getAttribute('aof:isAppEnsembleApp') == 'true':
                uri = e.getAttribute('aof:realizedBy')
                if uri != "":
                    self.required_apps.append(URIRef(uri))

    def create(self):
        graphStatus=GraphFactory(self).create()
        zipStatus=ZipFactory(self).create()
        Status=graphStatus.status+zipStatus.status
        if(Status==0):
            return statusReport(0)
        elif(Status<=2):
            return statusReport(1,self.returnWarnings())
        elif(graphStatus==3):
            return graphStatus
        else:
            return zipStatus


class GraphFactory():
    def __init__(self,factory):
        self.factory = factory
        self.g = ConjunctiveGraph(store=IOMemory(), identifier=self.factory.name)
        self.stat=0
        self.resp=""

    def _saveGraph(self):
        output=self.g.serialize(format="turtle")
        try:
            file = open((self.factory.tmp_path+".ttl"), 'wb')
            file.write(output)
            file.close()
        except:
            self.resp = "ttl-File is not writeable!"
            self.stat = 1

    def _bindRequiredApps(self):
        ap = AppPool.Instance()
        for app in self.factory.required_apps:
            self.g.add((appensemble, ORCHESTRATION.requiresApp, app))
            self.g = fill_graph_by_subject(ap, self.g, app)

    def _determineSequenceFlows(self):
        sf_in = self.factory.dom.getElementsByTagName('bpmn2:incoming')
        sf_out = self.factory.dom.getElementsByTagName('bpmn2:outgoing')
        sf = {}
        sf_tmp = {}

        for flow in sf_out:
            sf_tmp[flow.firstChild.nodeValue] = flow
        for flow in sf_in:
            sf[sf_tmp[flow.firstChild.nodeValue]] = flow.parentNode

        return sf

    # TODO: what if there are more starts?
    def _determineEntryPoint(self):
        start = self.factory.dom.getElementsByTagName('bpmn2:startEvent')
        for child in start[0].childNodes:
            if child.nodeName == 'bpmn2:outgoing':
                if sf[child].nodeName == 'bpmn2:userTask':
                    entryPoint = sf[child]
                    if entryPoint.attributes.__contains__('aof:isAppEnsembleApp'):
                        if entryPoint.attributes.__contains__('aof:realizedBy'):
                            return URIRef(entryPoint.attributes.__contains__('aof:realizedBy'))
                        else:
                            raise InconsistentAE("EntryPoint-App has no URI!")
                    else:
                        raise InconsistentAE("EntryPoint is no App!")

    def create(self):
        #AE = Namespace("http://eataof.et.tu-dresden.de/app-ensembles/" + self.factory.name + "/")

        self.g.bind("aof", AOF)
        self.g.bind("bpmn2", BPMN2)
        #self.g.bind("ae", AE)
        self.g.bind("o", ORCHESTRATION)

        # init nodes
        orchestration = BNode()
        appensemble = URIRef("http://eataof.et.tu-dresden.de/app-ensembles/" + self.factory.name + "/")

        # add Orchestration
        self.g.add((orchestration, RDF.type, ORCHESTRATION['Orchestration']))

        # add App-Ensemble
        self.g.add((orchestration, ORCHESTRATION.hasAppEnsemble, appensemble))
        self.g.add((appensemble, RDF.type, AOF['isAppEnsemble']))
        self.g.add((appensemble, ORCHESTRATION.Name, Literal(self.factory.name)))

        self.factory.registerLogEntry('##### Creation Logfile for ' + self.factory.name + ' App-Ensemble #####\n Date: ' + time.strftime(
                '%Y-%m-%d %H:%M:%S') + '\n')
        self.factory.registerLogEntry('### Creating the ttl-data out of XML')

        # Load app descriptions into graph
        self._bindRequiredApps()

        # create a mapping for sequenceFlows: f(outgoing-sequenceflow)=targetElement
        sf=self._determineSequenceFlows()

        try:
            # Determining the Entry Point and binding to the graph otherwise raise exceptions
            entryPoint=self._determineEntryPoint()
            self.g.add((appensemble, ORCHESTRATION.hasEntryPoint,entryPoint))

            # TODO go through the graph

            self.factory.registerLogEntry('> ttl-file successfully created\n> bpmn-file successfully created\n')

        except InconsistentAE as e:
            self.factory.registerLogEntry('!! ttl-file could not be finished because of: ' + str(e) + '\n')
            self.factory.registerWarning("ttl","TTL-File could not be finished!")
            self.stat=1
        self._saveGraph()


                    # self.g.add((appensemble,ORCHESTRATION.hasDefaultIntent,Literal("eu.comvantage.iaf.SIMPLE_MESSAGE")))


        return statusReport(self.stat,self.factory.name+": "+self.resp)

class ZipFactory():
    def __init__(self, factory):
        self.factory = factory
        self.ap=AppPool.Instance()
        self.app_tmp_path=[]
        registry = get_current_registry()
        self.destination=AssetResolver().resolve('{}/{}.ae'.format(registry.settings['app_ensemble_folder'],self.factory.name)).abspath()
        self.stat=0
        self.resp=""

    # TODO What if same appname but other content?
    def _downloadApps(self):
        self.factory.registerLogEntry('### Downloading the Apps\n')
        for app in self.factory.required_apps:
            uri = self.ap.get_install_uri(app)
            appname = uri.rsplit('/', 1)[-1]
            self.factory.registerLogEntry('# App "' + app + '"\n> install uri: ' + uri)
            try:
                tmp_path = tuple([appname])
                tmp_path += urlretrieve(uri)
                self.app_tmp_path.append(tmp_path)

                self.factory.registerLogEntry('> App was succesfully downloaded')
            except URLError:
                self.factory.registerLogEntry('!! App could not be downloaded')
                self.factory.registerWarning("apps","Not all Apps could be downloaded!")
                self.stat=1
            except ValueError:
                self.factory.registerLogEntry('!! App could not be found')
                self.factory.registerWarning("apps","Not all Apps could be downloaded!")
                self.stat=1

    def create(self):
        self.factory.registerLogEntry('### Creating the zip-file')
        self._downloadApps()
        try:
            with ZipFile(self.destination,'w') as myzip:
                myzip.write(self.factory.tmp_path + ".ttl", "ae.ttl")
                self.factory.registerLogEntry('> ttl-file successfully written\n')

                myzip.write(self.factory.tmp_path + ".bpmn", "ae.bpmn")
                self.factory.registerLogEntry('> bpmn-file successfully written\n')

                self.factory.registerLogEntry('\n# Copying the Apps\n')
                for fp in self.app_tmp_path:
                    myzip.write(fp[1], os.path.join('apps', fp[0]))
                    self.factory.registerLogEntry('> ' + fp[0] + ' successfully copied\n')
                #myzip.write(filepath + ".log", "log.txt")
            myzip.close()
        except IOError as e:
            self.resp = "App-Ensemble-File is not writeable!"
            self.stat = 3

        except OSError as e:
            self.resp = "Filepath doesn't exist!"
            self.stat = 3
        except:
            self.resp = "Unknown error while creating the App-Ensemble"
            self.stat = 3

        return statusReport(self.stat,self.factory.name+": "+self.resp)

class InconsistentAE(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

"""
    0: OK
    1: Warning
    3: Error
"""
class statusReport():
    def __init__(self,stat,resp=""):
        self.status=stat
        self.response=resp


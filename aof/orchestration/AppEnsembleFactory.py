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
import random,string,re

AOF = Namespace('http://eatld.et.tu-dresden.de/aof/')
BPMN2 = Namespace('http://dkm.fbk.eu/index.php/BPMN2_Ontology#')

class OrchestrationFactory():
    def __init__(self, bpmnxml,mode):
        self.mode=mode
        self.bpmn = bpmnxml
        self.dom = parseString(bpmnxml)
        self.appEnsembles = {}
        self.required_apps = []
        self.warnings = {}
        self.log = [];
        self.rand=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.tmp_path=AssetResolver().resolve('aof:tmp/ae-trash/'+self.rand).abspath()
        self._extractAppEnsembles()


    def _extractAppEnsembles(self):
        participants = self.dom.getElementsByTagName('bpmn2:participant')
        for p in participants:
            if (p.getAttribute('aof:isAppEnsemble')):
                try:
                    id=p.getAttribute('id')
                    self.appEnsembles[id] = {}
                    self.appEnsembles[id]["name"] = p.getAttribute('name').replace(" ","-")
                    self.appEnsembles[id]["processRef"] = p.getAttribute('processRef')
                    rand=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                    self.appEnsembles[id]["tmp_path"]=AssetResolver().resolve('aof:tmp/ae-trash/'+rand).abspath()
                except:
                    pass
        ks = list(self.appEnsembles)
        self.name=self.appEnsembles[ks[0]]["name"]
        self.AE = Namespace("http://eataof.et.tu-dresden.de/app-ensembles/" + self.name)
        processes = self.dom.getElementsByTagName('bpmn2:process')
        for p in processes:
            id = p.attributes['id'].nodeValue
            for ae in self.appEnsembles:
                if self.appEnsembles[ae]["processRef"] == id:
                    self.appEnsembles[ae]["dom"] = p
                    self.appEnsembles[ae]["requiredApps"]=self._extractRequiredApps(p)
        for id in self.appEnsembles:
            self.appEnsembles[id]["aenode"]=URIRef("ae:"+self.appEnsembles[id]["name"])
            self.appEnsembles[id]["graph"] = ConjunctiveGraph(store=IOMemory(), identifier=self.appEnsembles[id]["aenode"])

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
        graphStatus=statusReport(0)
        store=IOMemory()

        for ae in self.appEnsembles:
            self._saveBpmn(self.tmp_path)
            gf=GraphFactory(self,self.appEnsembles[ae])
            graphStatustmp=gf.create()
            graphStatus=statusReport(graphStatus.status+graphStatustmp.status,graphStatus.response+graphStatustmp.response)
            store.add_graph(gf.g)
        if len(self.appEnsembles)>1:
            trigGraph=ConjunctiveGraph(store=store)
            output=trigGraph.serialize(format="trig")
            try:
                file = open((self.tmp_path+".trig"), 'wb')
                file.write(output)
                file.close()
            except:
                self.resp = "trig-File is not writeable!"
                self.stat = 1

        zipStatus=ZipFactory(self).create(len(self.appEnsembles))
        Status=graphStatus.status+zipStatus.status

        if(Status==0):
            response= statusReport(0)
        elif(Status<=2):
            response= statusReport(1,self.returnWarnings())
        elif(graphStatus==3):
            response= graphStatus
        else:
            response= zipStatus

        text+=response.response+"\n"
        status =response.status

        if(status==0):
            return Response("Orchestration sucessfully created!","201 Created")
        if (status<=len(self.appEnsembles)):
            return Response("Orchestration sucessfully created!"+text,"201 Created")
        else:
            return Response(text,"500 Internal Server Error")

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

    def registerLogEntry(self, type, message):
        # type 0=item, 1=sub-message, 2=sub-warning
        self.log.append({'time':time.strftime('%Y-%m-%d %H:%M:%S'),'type':type, 'msg':message})

    def saveLog(self,destination):
        logfile = open(destination, 'w')
        logfile.write('##### Creation Logfile for ' + self.name + ' App-Ensemble #####\n Date: ' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n\n')
        for line in self.log:
            if line['type']==1:
                logfile.write('\t > '+line['msg']+'\n')
            elif line['type']==2:
                logfile.write('\t ! '+line['msg']+'\n')
            else:
                logfile.write(line['time']+'\t'+line['msg']+'\n')
        logfile.close()

    def _extractRequiredApps(self,dom):
        required_apps=[]
        for e in dom.getElementsByTagName('bpmn2:userTask'):
            if e.getAttribute('aof:isAppEnsembleApp') == 'true':
                uri = e.getAttribute('aof:realizedBy')
                if uri != "":
                    required_apps.append(URIRef(uri))
        return required_apps



class GraphFactory():
    def __init__(self,factory,appEnsemble):
        self.factory = factory
        self.ae=appEnsemble
        self.g = self.ae["graph"]
        self.stat=0
        self.resp=""
        self.AENode=self.ae["aenode"]
        self.elements = self.ae["dom"].getElementsByTagName('*')

    def _saveGraph(self):
        output=self.g.serialize(format="turtle")
        try:
            file = open((self.ae["tmp_path"]+".ttl"), 'wb')
            file.write(output)
            file.close()
        except:
            self.resp = "ttl-File is not writeable!"
            self.stat = 1

    def _bindRequiredApps(self):
        ap = AppPool.Instance()
        for app in self.ae["requiredApps"]:
            self.g.add((self.AENode, AOF.requiresApp, app))
            self.g = fill_graph_by_subject(ap, self.g, app)

    def _setEntryPoints(self,type='url'):
        starts = self.ae["dom"].getElementsByTagName('bpmn2:startEvent')
        for start in starts:
             self.g.add((self.AENode, AOF.hasEntryPoint,URIRef('ae:'+start._attrs['id'].nodeValue)))

    def _getTaskUri(self,node,string=False):
        if node.attributes.__contains__('aof:isAppEnsembleApp'):
            if node.attributes.__contains__('aof:realizedBy'):
                if string:
                    return node.attributes['aof:realizedBy'].value
                else:
                    return URIRef(node.attributes['aof:realizedBy'].value)
            else:
                raise InconsistentAE("Task has no URI!")
        else:
            raise InconsistentAE("Task is no App!")


    def _addAppInstances(self):

        tasks = self.ae["dom"].getElementsByTagName('bpmn2:userTask')

        for task in tasks:
            nid=task._attrs['id'].nodeValue
            try:
                nodename=task._attrs['name'].nodeValue
            except:
                nodename=nid
                task._attrs['name']=nid
            node=URIRef('ae:'+nid)
            self.g.add((node,BPMN2.id, Literal(task._attrs['id'].nodeValue) ))
            self.g.add((node,BPMN2.Name, Literal(nodename)))

            self.g.add((node,RDF.type, AOF.userTask))
            try:
                instanceURI=self._getTaskUri(task)
                self.g.add((node,AOF.assignedApp, instanceURI))
            except:
                pass

        regex=re.compile("^(.*(t|manualT)ask.*)$")
        tasks=[el for el in self.elements for m in [regex.search(el.nodeName)] if m]

        for task in tasks:
            nid=task._attrs['id'].nodeValue
            try:
                nodename=task._attrs['name'].nodeValue
            except:
                nodename=nid
                task._attrs['name']=nid

            node=URIRef('ae:'+nid)
            self.g.add((node,BPMN2.id, Literal(task._attrs['id'].nodeValue) ))
            self.g.add((node,BPMN2.Name, Literal(nodename)))
            self.g.add((node,RDF.type, URIRef(BPMN2+task.localName)))

    def _addGatewayInstances(self):
        regex=re.compile("^(.*(G|g)ateway.*)$")
        gateways=[el for el in self.elements for m in [regex.search(el.nodeName)] if m]

        for gateway in gateways:
            node=URIRef('ae:'+gateway._attrs['id'].nodeValue)
            self.g.add((node,BPMN2.id, Literal(gateway._attrs['id'].nodeValue) ))
            self.g.add((node,RDF.type, URIRef(BPMN2+gateway.localName)))
            children=gateway.getElementsByTagName('*')
            for child in children:
                self.g.add((node,URIRef(BPMN2+child.localName), URIRef("ae:"+child.firstChild.nodeValue) ))

    def _addSequenceFlowInstances(self):
        regex=re.compile("^(.*sequenceFlow.*)$")
        sfs=[el for el in self.elements for m in [regex.search(el.nodeName)] if m]

        for sf in sfs:
            node=URIRef('ae:'+sf._attrs['id'].nodeValue)
            self.g.add((node,BPMN2.id, Literal(sf._attrs['id'].nodeValue) ))
            self.g.add((node,RDF.type, URIRef(BPMN2+sf.localName)))
            self.g.add((node,BPMN2.sourceRef, URIRef('ae:'+sf._attrs['sourceRef'].nodeValue) ))
            self.g.add((node,BPMN2.targetRef, URIRef('ae:'+sf._attrs['targetRef'].nodeValue) ))

    def _addEventInstances(self):
        regex=re.compile("^(.*(E|e)vent.*)$")
        sfs=[el for el in self.elements for m in [regex.search(el.nodeName)] if m]

        for sf in sfs:
            node=URIRef('ae:'+sf._attrs['id'].nodeValue)
            self.g.add((node,BPMN2.id, Literal(sf._attrs['id'].nodeValue) ))
            self.g.add((node,RDF.type, URIRef(BPMN2+sf.localName)))
            children=sf.getElementsByTagName('*')
            for child in children:
                self.g.add((node,URIRef(BPMN2+child.localName), URIRef("ae:"+child.firstChild.nodeValue) ))

    def create(self):

        self.g.bind("aof", AOF)
        self.g.bind("bpmn2", BPMN2)
        self.g.bind("ae", self.factory.AE)

        # add App-Ensemble
        self.g.add((self.AENode, RDF.type, AOF.isAppEnsemble))
        self.g.add((self.AENode, AOF.Name, Literal(self.ae["name"])))

        self.factory.registerLogEntry(0,'Creating the ttl-data out of XML')

        try:
            # Load app descriptions into graph
            self._bindRequiredApps()

            # Add Structure instances
            self._addAppInstances()
            self._addGatewayInstances()
            self._addEventInstances()
            self._addSequenceFlowInstances()

            # Determining the Entry Point and binding to the graph otherwise raise exceptions
            self._setEntryPoints()

            self.factory.registerLogEntry(1,'ttl-file successfully created\n> bpmn-file successfully created\n')

        except InconsistentAE as e:
            self.factory.registerLogEntry(2,'ttl-file could not be finished because of: ' + str(e))
            self.factory.registerWarning("ttl","TTL-File could not be finished!")
            self.stat=1
        self._saveGraph()

        return statusReport(self.stat,self.ae["name"]+": "+self.resp)

class ZipFactory():
    def __init__(self, factory):
        self.factory = factory
        self.ap=AppPool.Instance()
        self.app_tmp_path=[]
        self.stat=0
        self.resp=""

    # TODO What if same appname but other content?
    def _downloadApps(self):
        self.factory.registerLogEntry(0,'Downloading the Apps')
        for ae in self.factory.appEnsembles:
            for app in self.factory.appEnsembles[ae]["requiredApps"]:
                uri = self.ap.get_install_uri(app)
                appname = uri.rsplit('/', 1)[-1]
                self.factory.registerLogEntry(0,'App "' + app + '"')
                self.factory.registerLogEntry(1,'install uri: ' + uri)
                try:
                    tmp_path = tuple([appname])
                    tmp_path += urlretrieve(uri)
                    self.app_tmp_path.append(tmp_path)

                    self.factory.registerLogEntry(1,'App was succesfully downloaded')
                except URLError:
                    self.factory.registerLogEntry(2,'App could not be downloaded')
                    self.factory.registerWarning("apps","Not all Apps could be downloaded!")
                    self.stat=1
                except ValueError:
                    self.factory.registerLogEntry(2,'App could not be found')
                    self.factory.registerWarning("apps","Not all Apps could be downloaded!")
                    self.stat=1

    def create(self,len=1):
        self.factory.registerLogEntry(0,'Creating the zip-file')
        self._downloadApps()
        registry = get_current_registry()
        destination=AssetResolver().resolve('{}/{}.ae'.format(registry.settings['app_ensemble_folder'],self.factory.name)).abspath()
        if os.path.isfile(destination) and self.factory.mode !='edit':
            destination=AssetResolver().resolve('{}/{}-{}.ae'.format(registry.settings['app_ensemble_folder'],self.factory.name,self.factory.rand)).abspath()
        try:


            with ZipFile(destination,'w') as myzip:
                if len>1:
                    multiplier=0
                    myzip.write(self.factory.tmp_path + ".trig", "ae.trig")
                    self.factory.registerLogEntry(0,'ttl-file successfully written')
                else:
                    multiplier=""
                for ae in self.factory.appEnsembles:
                    if len>1:
                        multiplier+=1
                    myzip.write(self.factory.appEnsembles[ae]["tmp_path"] + ".ttl", "ae"+str(multiplier)+".ttl")
                    self.factory.registerLogEntry(0,'ttl-file successfully written')

                myzip.write(self.factory.tmp_path + ".bpmn", "ae.bpmn")
                self.factory.registerLogEntry(0,'bpmn-file successfully written')

                self.factory.registerLogEntry(0,'Copying the Apps')
                for fp in self.app_tmp_path:
                    myzip.write(fp[1], os.path.join('apps', fp[0]))
                    self.factory.registerLogEntry(1,fp[0] + ' successfully copied')
                self.factory.saveLog(self.factory.tmp_path + ".log")
                myzip.write(self.factory.tmp_path + ".log", "log.txt")
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


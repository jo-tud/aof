from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from pyramid.path import AssetResolver
from aof.orchestration.AppEnsemblePool import AppEnsemblePool
from aof.orchestration.AppPool import AppPool
from aof.views.PageViews import PageViews,RequestPoolURI_Decorator
from urllib.parse import quote
import logging,shutil,os

__author__ = 'khoerfurter'
log = logging.getLogger(__name__)


class AppEnsembleViews(PageViews):
    """
    Class with all AppEnsemble-Pages and -Actions
    """

    def __init__(self, context, request):
        super(AppEnsembleViews, self).__init__(context, request)
        self.pool = AppEnsemblePool.Instance()

    @view_config(route_name='app-ensembles', renderer='aof:templates/ae.mako')
    def page_overview(self):
        """
        Generates the parameters for the AppEnsemble-Homepage
        """
        self._setTitle('App-Ensembles')
        return self._returnCustomDict()

    @view_config(route_name='api-appensembles', renderer='json')
    def api_json(self):
        """
        Generates the pool in Json
        :return: json-representation of the AppEnsemble-Pool
        """
        ae_info = dict()
        try:
            for key in self.pool.get_all_AppEnsembles():
                ae = self.pool.get_AppEnsemble(key)
                path = ae.ae_pkg_path
                apps = ae.getRequiredApps().serialize(format='json').decode()
                ae_info[key] = {'uri': key, 'path': path, 'apps': apps}
        except AttributeError:
            ae_info[key] = {'uri': key, 'path': path, 'apps': {}}
        return ae_info

    @view_config(route_name='api-action-appensembles-update')
    def action_update(self):
        """
        Action: Update the AppEnsemblePool from current AppEnsemble-directory
        :return: Response Object with number of Apps
        """
        self.pool.reload()
        resp = str(len(self.pool))
        return Response(resp)

    #TODO: Add documentation and make info if the request was successful visible
    @view_config(route_name='api-action-appensembles-add')
    def api_action_add(self):
        """
        Action: Update the AppEnsemblePool from current AppEnsemble-directory
        :return: Response Object with number of Apps
        """
        from xml.dom.minidom import parseString, NodeList
        from rdflib import ConjunctiveGraph, URIRef, BNode, Literal, RDF, RDFS, Namespace
        from rdflib.plugins.memory import IOMemory
        from zipfile import ZipFile
        import time
        from urllib.request import urlretrieve
        from urllib.error import URLError
        from aof.views.AppPoolViews import fill_graph_by_subject

        class InconsistentAE(Exception):
            def __init__(self, value):
                self.value = value
            def __str__(self):
                return repr(self.value)



        if self.request.params.has_key('data') and self.request.params.getone('data')!="":
            data = self.request.params.getone('data')

            AOF = Namespace('http://eatld.et.tu-dresden.de/aof/')
            BPMN2 = Namespace ('http://dkm.fbk.eu/index.php/BPMN2_Ontology#')
            ORCHESTRATION = Namespace ('http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#')

            dom = parseString(data)

            participants=dom.getElementsByTagName('bpmn2:participant')
            name="unnamed"
            for p in participants:
                if(p.getAttribute('aof:isAppEnsemble')):
                    try:
                        name=p.getAttribute('name').replace(" ","-")
                        appEnsembleId=p.getAttribute('processRef')
                        break
                    except:
                        pass

            AE = Namespace("http://eataof.et.tu-dresden.de/app-ensembles/"+name+"/")
            filepath=AssetResolver().resolve('aof:tmp/ae-trash/{}'.format(name)).abspath() # tmp-path for all ae-files

            logfile = open(filepath+'.log', 'w')
            logfile.writelines(['##### Creation Logfile for '+name+' App-Ensemble #####\n', 'Date: '+time.strftime('%Y-%m-%d %H:%M:%S'), '\n'])
            warnings = {}

            linked_apps=[];
            for e in dom.getElementsByTagName('bpmn2:userTask'):
                if e.getAttribute('aof:isAppEnsembleApp')== 'true':
                    uri=e.getAttribute('aof:realizedBy')
                    if uri!="":
                        linked_apps.append(URIRef(uri))


            #if processes.__len__() > 1:
                #print("There is more than one process (" + processes.__len__().__str__() + ")")

            store = IOMemory()
            graph=ConjunctiveGraph(store=store)
            ap=AppPool.Instance()

            logfile.writelines(['\n\n### Creating the ttl-data out of XML\n'])
            try:
                processes = dom.getElementsByTagName('bpmn2:process')

                for p in processes:
                    id=p.attributes['id'].nodeValue
                    if id==appEnsembleId:
                        g = ConjunctiveGraph(store=store,identifier=URIRef(AE[id]))
                        g.bind("aof", AOF)
                        g.bind("bpmn2", BPMN2)
                        g.bind("ae",AE)
                        g.bind("o",ORCHESTRATION)

                        # init Blank nodes
                        orchestration=BNode()
                        appensemble=BNode()
                        #add Orchestration
                        g.add((orchestration,RDF.type,ORCHESTRATION['Orchestration']))
                        # add App-Ensemble
                        g.add((orchestration,ORCHESTRATION.hasAppEnsemble,appensemble))
                        g.add((appensemble,RDF.type,AOF['isAppEnsemble']))
                        g.add((appensemble,ORCHESTRATION.Name,Literal(name)))

                        #g.add((appensemble,ORCHESTRATION.hasDefaultIntent,Literal("eu.comvantage.iaf.SIMPLE_MESSAGE")))

                        # Load app descriptions into graph
                        for app in linked_apps:
                            g.add((appensemble,ORCHESTRATION.requiresApp,app))
                            g = fill_graph_by_subject(ap, g, app)

                        # create a mapping for sequenceFlows: f(outgoing-sequenceflow)=targetElement
                        sf_in=dom.getElementsByTagName('bpmn2:incoming')
                        sf_out=dom.getElementsByTagName('bpmn2:outgoing')
                        sf = {}
                        sf_tmp={}

                        for flow in sf_out:
                            sf_tmp[flow.firstChild.nodeValue]=flow
                        for flow in sf_in:
                            sf[sf_tmp[flow.firstChild.nodeValue]]=flow.parentNode

                        # Determining the Entry Point and binding to the graph otherwise raise exceptions
                        start=dom.getElementsByTagName('bpmn2:startEvent')
                        for child in start[0].childNodes:       # TODO: what if there are more starts?
                            if child.nodeName=='bpmn2:outgoing':
                                if sf[child].nodeName=='bpmn2:userTask':
                                    entryPoint=sf[child]
                                    if entryPoint.attributes.__contains__('aof:isAppEnsembleApp'):
                                        if entryPoint.attributes.__contains__('aof:realizedBy'):
                                            g.add((appensemble,ORCHESTRATION.hasEntryPoint,URIRef(entryPoint.attributes.__contains__('aof:realizedBy'))))
                                        else:
                                            raise InconsistentAE("EntryPoint-App has no URI!")
                                    else:
                                        raise InconsistentAE("EntryPoint is no App!")

                        # TODO go through the graph
                        # TODO move to an own class out of views

                        # go on
                        # g.add((AE[name],RDF.type,BPMN2['process']))
                        #
                        #
                        # for attrName, attrValue in p.attributes.items():
                        #     g.add((AE[name], BPMN2[attrName], Literal(attrValue)))
                        #
                        # for element in p.childNodes:
                        #     if element.nodeType == Node.ELEMENT_NODE:
                        #         id = element.attributes['id'].nodeValue
                        #
                        #         g.add((AE[id], RDFS.subClassOf, URIRef(BPMN2[element.localName])))
                        #
                        #         for attrName, attrValue in element.attributes.items():
                        #             g.add((AE[id], BPMN2[attrName], Literal(attrValue)))
                        #
                        #         for sub_element in element.childNodes:
                        #             if sub_element.nodeType == Node.ELEMENT_NODE:
                        #                 g.add((AE[id], BPMN2[sub_element.localName], AE[sub_element.firstChild.nodeValue]))
            except InconsistentAE as e:
                logfile.writelines(['!! ttl-file could not be finished because of: '+str(e)+'\n'])
                warnings["ttl"]="TTL-File could not be finished!"

            logfile.writelines(['\n\n### Downloading the Apps\n'])
            filepathes=[]
            for app in linked_apps:
                uri=ap.get_install_uri(app)
                appname=uri.rsplit('/', 1)[-1]
                logfile.writelines(['\n# App "'+app+'"\n','> install uri: '+uri+'\n'])
                try:
                    tmp_path=tuple([appname])
                    tmp_path+=urlretrieve(uri)
                    filepathes.append(tmp_path)
                    logfile.writelines(['> App was succesfully downloaded\n'])
                except URLError:
                    logfile.writelines(['!! App could not be downloaded\n'])
                    warnings["apps"]="Not all Apps could be downloaded!"

            output=graph.serialize(format="turtle")


            logfile.writelines(['\n\n### Creating the zip-file\n'])
            try:
                file = open(filepath+".ttl", 'wb')
                file.write(output);
                file.close()
                file = open(filepath+".bpmn", 'wb')
                file.write(bytes(data,"utf-8"));
                file.close()
                logfile.writelines(['> ttl-file successfully created\n','> bpmn-file successfully created\n'])

                with ZipFile(AssetResolver().resolve('{}/{}.ae'.format(self.request.registry.settings['app_ensemble_folder'],name)).abspath(), 'w') as myzip:
                    myzip.write(filepath+".ttl","ae.ttl")
                    logfile.writelines(['> ttl-file successfully written\n'])

                    myzip.write(filepath+".bpmn","ae.bpmn")
                    logfile.writelines(['> bpmn-file successfully written\n'])

                    logfile.writelines(['\n# Copying the Apps\n'])
                    for fp in filepathes:
                        myzip.write(fp[1],os.path.join('apps',fp[0]))
                        logfile.writelines(['> '+fp[0]+' successfully copied\n'])

                    logfile.close()
                    myzip.write(filepath+".log","log.txt")
                myzip.close()

                resp="The App-Ensemble was successfully saved!"
                if len(warnings)>0:
                    resp +="<br><br><strong>Warnings:</strong><ul>"
                    for w in warnings:
                        resp +="<li>"+warnings[w]+"</li>"
                    resp +="</ul>Please watch the Logfile stored in the AppEnsemble!"
                stat="201 Created"

            except IOError as e:
                resp="App-Ensemble-File is not writeable!"
                stat="500 Internal Server Error"

            except OSError as e:
                resp="Filepath doesn't exist!"
                stat="500 Internal Server Error"
            except:
                resp="Unknown error while creating the App-Ensemble"
                stat="500 Internal Server Error"
        else:
            resp="There was no data attached!"
            stat="400 Bad Request"

        self.pool.reload()
        return Response(resp,stat)

    @view_config(route_name='ae-details', renderer='aof:templates/ae-details.mako')
    @RequestPoolURI_Decorator()
    def page_details(self):
        """
        Generates the Detail-Attributes for an given Request-URI
        :return: dictionary
        """
        self._setTitle('App-Ensemble Details')

        return self._returnCustomDict(self.api_page_details())

    @view_config(route_name='api-appensembles-ae', renderer='json')
    @RequestPoolURI_Decorator()
    def api_page_details(self):
        ae = self.pool.get_AppEnsemble(self.uri)
        api_ae_uri=self.build_URI('api-appensembles-ae-package','{URI:.*}',self.uri)

        ae_apps = ae.getRequiredApps(use_json=True)
        custom_args = {
            'ae_uri': self.uri,
            'ae_api_path':api_ae_uri,
            'qrcode': self.pool.get_QRCode(api_ae_uri),
            'direct_download_uri':self.build_URI('api-appensembles-ae-package',"{URI:.*}",self.uri),
            'ae_has_bpm': ae.has_bpm(),
            'ae_apps': ae_apps,
            'bpmn_view_uri':self.build_URI('ae-view-bpm',"{URI}",self.uri),
            'bpmn_edit_uri':self.build_URI('ae-edit-bpm',"{URI}",self.uri),
            'bpmn_delete_uri':self.build_URI('api-appensembles-delete',"{URI}",self.uri)
        }
        return custom_args

    @view_config(route_name='ae-create-bpm', renderer='aof:templates/ae-bpm-modeler.mako')
    def page_create_bpm(self):
        """
        Generates the BPMN-Visualisation Page
        :return: dictionary
        """
        custom_args={
            'mode':"",
            'urlencodedXML':""
        }
        self._setTitle('Create App-Ensemble')
        return self._returnCustomDict(custom_args)

    #TODO: Edit overright the BPM with same ae-name.... check that
    @view_config(route_name='ae-edit-bpm', renderer='aof:templates/ae-bpm-modeler.mako')
    @RequestPoolURI_Decorator()
    def page_edit_bpm(self):
        """
        Generates the BPMN-Visualisation Page
        :return: dictionary
        """
        ae = self.pool.get_AppEnsemble(self.uri)
        custom_args={
            'mode':"edit",
            'urlencodedXML':quote(ae.get_bpm())
        }
        self._setTitle('App-Ensemble Details | Edit BPMN')
        return self._returnCustomDict(custom_args)

    @view_config(route_name='ae-view-bpm', renderer='aof:templates/ae-bpm-modeler.mako')
    @RequestPoolURI_Decorator()
    def page_view_bpm(self):
        """
        Generates the BPMN-Visualisation Page
        :return: dictionary
        """
        ae = self.pool.get_AppEnsemble(self.uri)
        custom_args={
            'mode':"view",
            'urlencodedXML':quote(ae.get_bpm())
        }
        self._setTitle('App-Ensemble Details | BPMN')
        return self._returnCustomDict(custom_args)

    @view_config(route_name='api-appensembles-ae-bpmn')
    @RequestPoolURI_Decorator()
    def api_action_get_bpmn_data(self):
        """
        Generates the BPMN-Data for visulisation
        :return: Response with the BPMN-xml
        """
        ae = self.pool.get_AppEnsemble(self.uri)
        bpmn = ae.get_bpm()
        response = Response(
            body=bpmn,
            request=self.request,
            content_type='txt/xml'
        )
        response.content_disposition = 'attachement; filename="' + str(self.uri) + ".bpmn"
        return response

    @view_config(route_name='api-appensembles-ae-package')
    @RequestPoolURI_Decorator()
    def action_get_ae_pkg(self):
        """
        Generates the AppEnsemble-package for downloading
        :return: Response with AppEnsemble-package
        """
        ae = self.pool.get_AppEnsemble(self.uri)
        response = FileResponse(
            ae.ae_pkg_path,
            request=self.request,
            content_type='application/vnd.aof.package-archive'
        )
        response.content_disposition = 'attachement; filename="' + str(self.uri) + ".ae"
        return response

    @view_config(route_name='api-appensembles-delete', renderer='aof:templates/ae-bpm-modeler.mako')
    @RequestPoolURI_Decorator()
    def api_action_ae_delete(self):
        """
        Moves the App-Ensemble into tmp-folder
        :return: Response-Object
        """
        a=AssetResolver()
        ae_filename='{}.ae'.format(self.uri)
        source=a.resolve(os.path.join(self.request.registry.settings['app_ensemble_folder'],ae_filename)).abspath()
        dest=a.resolve(os.path.join('aof:tmp','ae-trash',ae_filename)).abspath()
        i=0
        while(os.path.isfile(dest)):
            i+=1
            dest=a.resolve(os.path.join('aof:tmp','ae-trash','{}-{}.ae'.format(self.uri,i))).abspath()
        shutil.move(source,dest)
        resp="The App-Ensemble was moved into the trash and will be deleted at next System startup."
        self.pool.reload()
        return Response(resp)
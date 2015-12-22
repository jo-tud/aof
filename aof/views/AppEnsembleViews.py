from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from pyramid.path import AssetResolver
from aof.orchestration.AppEnsemblePool import AppEnsemblePool
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
        from xml.dom.minidom import parseString, Node
        from rdflib import ConjunctiveGraph, URIRef, BNode, Literal, RDF, RDFS, Namespace
        from rdflib.plugins.memory import IOMemory
        from zipfile import ZipFile

        if self.request.params.has_key('data') and self.request.params.getone('data')!="":
            data = self.request.params.getone('data')

            AOF = Namespace('http://eatld.et.tu-dresden.de/aof/')
            BPMN2 = Namespace ('http://dkm.fbk.eu/index.php/BPMN2_Ontology#')

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


            processes = dom.getElementsByTagName('bpmn2:process')

            #if processes.__len__() > 1:
                #print("There is more than one process (" + processes.__len__().__str__() + ")")

            store = IOMemory()
            graph=ConjunctiveGraph(store=store)

            for p in processes:
                id=p.attributes['id'].nodeValue
                if id==appEnsembleId:
                    g = ConjunctiveGraph(store=store,identifier=URIRef(AE[id]))
                    g.bind("aof", AOF)
                    g.bind("bpmn2", BPMN2)
                    g.bind("ae",AE)

                    g.add((AE[name],RDF.type,BPMN2['process']))
                    g.add((AE[name],RDF.type,AOF['AppEnsemble']))

                    for attrName, attrValue in p.attributes.items():
                        g.add((AE[name], BPMN2[attrName], Literal(attrValue)))

                    for element in p.childNodes:
                        if element.nodeType == Node.ELEMENT_NODE:
                            id = element.attributes['id'].nodeValue

                            g.add((AE[id], RDFS.subClassOf, URIRef(BPMN2[element.localName])))

                            for attrName, attrValue in element.attributes.items():
                                g.add((AE[id], BPMN2[attrName], Literal(attrValue)))

                            for sub_element in element.childNodes:
                                if sub_element.nodeType == Node.ELEMENT_NODE:
                                    g.add((AE[id], BPMN2[sub_element.localName], AE[sub_element.firstChild.nodeValue]))

            output=graph.serialize(format="trig")



            try:
                filepath=AssetResolver().resolve('aof:tmp/{}'.format(name)).abspath()
                file = open(filepath+".trig", 'wb')
                file.write(output);
                file.close()
                file = open(filepath+".bpmn", 'wb')
                file.write(bytes(data,"utf-8"));
                file.close()
                with ZipFile(AssetResolver().resolve('{}/{}.ae'.format(self.request.registry.settings['app_ensemble_folder'],name)).abspath(), 'w') as myzip:
                    myzip.write(filepath+".trig","ae.trig")
                    myzip.write(filepath+".bpmn","ae.bpmn")
                myzip.close()

            except IOError as e:
                resp="Could not save AppEnsemble!"
                stat="500 Internal Server Error"

            resp="The AppEnsemble was successfully saved!"
            stat="201 Created"
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
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

        from aof.orchestration.AppEnsembleFactory import OrchestrationFactory

        if self.request.params.has_key('mode') and self.request.params.getone('mode')!="":
            mode=self.request.params.getone('mode')
        else:
            mode=''
        if self.request.params.has_key('del') and self.request.params.getone('del')!="":
            self.helper_delete_ae(self.request.params.getone('del'))

        if self.request.params.has_key('data') and self.request.params.getone('data')!="":
            self.api_action_ae_delete();
            response=OrchestrationFactory(self.request.params.getone('data'),mode).create()
            self.pool.reload()
        else:
            response=Response("There was no data attached!","400 Bad Request")


        return response

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
            'urlencodedXML':"",
            'uri':""
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
            'urlencodedXML':quote(ae.get_bpm()),
            'uri':self.uri
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
        resp=self.helper_delete_ae(self.uri)
        self.pool.reload()
        return Response(resp["resp"])

    def helper_delete_ae(self,uri):
        a=AssetResolver()
        ae_filename='{}.ae'.format(uri)
        source=a.resolve(os.path.join(self.request.registry.settings['app_ensemble_folder'],ae_filename)).abspath()
        dest=a.resolve(os.path.join('aof:tmp','ae-trash',ae_filename)).abspath()
        i=0
        while(os.path.isfile(dest)):
            i+=1
            dest=a.resolve(os.path.join('aof:tmp','ae-trash','{}-{}.ae'.format(uri,i))).abspath()
        try:
            shutil.move(source,dest)
            resp="The App-Ensemble was moved into the trash and will be deleted at next System startup."
            stat="0"
        except:
            resp="The Name of the App-Ensembe has changed. Please close the current App-Ensemble!"
            stat="1"

        return {'resp':resp,'stat':stat}

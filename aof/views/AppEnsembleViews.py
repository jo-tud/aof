from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from aof.orchestration.AppEnsemblePool import AppEnsemblePool
from aof.views.PageViews import PageViews,RequestPoolURI_Decorator
import logging

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

    @view_config(route_name='action-update-ap-ensembles')
    def action_update(self):
        """
        Action: Update the AppEnsemblePool from current AppEnsemble-directory
        :return: Response Object with number of Apps
        """
        self.pool.reload()
        resp = str(len(self.pool))
        return Response(resp)

    @view_config(route_name='ae-details', renderer='aof:templates/ae-details.mako')
    @RequestPoolURI_Decorator()
    def page_details(self):
        """
        Generates the Detail-Attributes for an given Request-URI
        :return: dictionary
        """
        self._setTitle('App-Ensemble Details')
        ae = self.pool.get_AppEnsemble(self.uri)


        api_ae_uri=self.build_URI('api-appensembles-ae-package','{URI:.*}',self.uri)

        ae_apps = ae.getRequiredApps().bindings
        custom_args = {
            'ae_uri': self.uri,
            'ae_api_path':api_ae_uri,
            'qrcode': self.pool.get_QRCode(api_ae_uri),
            'ae_has_bpm': ae.has_bpm(),
            'ae_apps': ae_apps,
            'bpmn_uri':self.build_URI('ae-visualize-bpm',"{URI}",self.uri)
        }
        return self._returnCustomDict(custom_args)

    @view_config(route_name='ae-visualize-bpm', renderer='aof:templates/ae-visualize-bpm.mako')
    @RequestPoolURI_Decorator()
    def page_visualize_bpm(self):
        """
        Generates the BPMN-Visualisation Page
        :return: dictionary
        """
        self._setTitle('App-Ensemble Details | BPMN')
        ae = self.pool.get_AppEnsemble(self.uri)
        custom_args = {
            'ae_path': ae.ae_pkg_path,
            'ae_uri': self.uri,
            'ae_has_bpmn': ae.has_bpm()
        }
        return self._returnCustomDict(custom_args)

    @view_config(route_name='api-appensembles-ae-bpmn')
    @RequestPoolURI_Decorator()
    def action_get_bpmn_data(self):
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
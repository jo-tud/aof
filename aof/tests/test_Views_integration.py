import unittest
from pyramid import testing

import aof.views as views
from pyramid.events import ApplicationCreated
from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool
from aof.tests.test_AppEnsemble import AppEnsembleTests
from aof.orchestration.AppEnsemble import AppEnsemble
from aof.orchestration.AppEnsembleManager import AppEnsembleManager
from webob.multidict import MultiDict
from pyramid.response import Response,FileResponse
from pyramid.httpexceptions import HTTPNotFound



class IntegrationViewTests(unittest.TestCase):
    def setUp(self):
        from pyramid.path import AssetResolver
        from aof.orchestration.AppPool import AppPool

        # import aof

        self.config = testing.setUp()


        #Setting up Test-AppPool
        a = AssetResolver()
        self.path = a.resolve('aof:tests/res/test_pool.ttl').abspath()
        self.ap = AppPool.Instance()
        self.ap.add_apps_from_app_pool_definition(source=self.path, format="turtle")

        #Setting up Test-AppEnsemble
        AppEnsembleTests._createTestArchive(self)

        # Setting up request and context
        self.request = testing.DummyRequest()
        self.context = testing.DummyResource()


    def tearDown(self):
        testing.tearDown()
        AppEnsembleTests._deleteTestArchive(self)


    # Private functionality

    def _meta_test(self, meta):
        self.assertIsInstance(meta['acronym'], str, 'Home View: Meta-acronym is not a string!')
        self.assertTrue(len(meta['acronym']) > 0, 'Home View:Meta-acronym does not exist!')

        self.assertTrue(len(meta['appname']) > 0, 'Home View:Meta-appname does not exist!')
        self.assertIsInstance(meta['appname'], str, 'Home View: meta-appname is not a string!')

    def _pagetitle_test(self, page_title):
        self.assertTrue(len(page_title) > 0, 'Page Title does not exist!')
        self.assertIsInstance(page_title, str, 'Page Title is not a string!')

    def _standard_tests(self, response):
        #Tests page title and meta-data

        self._pagetitle_test(response['page_title'])
        self._meta_test(response['meta'])

    # Private functionality: URI-Testing

    def _URI_error_tests(self,view_to_test,delete_tests=list()):
        #Testing for all URI-Errors
        self.view_to_test=view_to_test
        test_list=['_noURI_test','_emptyURI_test','_tooMuchURI_butOK_test','_tooMuchURI_test','_wrongURI_test']

        for dels in delete_tests:
            test_list.remove(dels)

        for x in test_list:
            self.request.params = MultiDict()
            getattr(self,x)()

        del(self.view_to_test)


    def _call_view_to_test(self):
        return getattr(getattr(views,self.viewclass_to_test)(self.context, self.request),self.view_to_test)()

    def _noURI_test(self):
        response = self._call_view_to_test()
        self.assertTrue('not supplied' in response.text)
        self.assertTrue(int(response.headers.get('Content-Length')) < 500)

    def _emptyURI_test(self):
        self.request.params.add('URI', '')

        response = self._call_view_to_test()
        self.assertTrue('"URI"-parameter was empty' in response.text)
        self.assertTrue(int(response.headers.get('Content-Length')) < 500)

    def _tooMuchURI_butOK_test(self):
        self.request.params.add('URI', 'testAppEnsemble')
        self.request.params.add('uri', 'testAppEnsemble2')

        response = self._call_view_to_test()
        self.assertNotIsInstance(response, Response,"Error in "+self.view_to_test+"!")

    def _tooMuchURI_test(self):
        self.request.params.add('URI', 'testAppEnsemble')
        self.request.params.add('URI', 'testAppEnsemble2')

        response = self._call_view_to_test()
        self.assertTrue('More than one URI' in response.text)
        self.assertTrue(int(response.headers.get('Content-Length')) < 500)

    def _wrongURI_test(self):
        self.request.params.add('URI', 'testAppEnsemblewhichdoesnotexist')

        response = self._call_view_to_test()
        self.assertIsInstance(response, HTTPNotFound,"Error in "+self.view_to_test+"!")



    # General view tests

    def test_home_view(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        response = views.home_view(context, request)

        self.assertTrue(int(response['number_of_apps']) > 0, 'Home View: AppPool is not initialized correctly!')
        self.assertIsInstance(response['number_of_apps'], str, 'Home View: Number of Apps is not a string!')

        self.assertTrue(int(response['number_of_ae']) > 0, 'Home View:AppEnsembles are not initialized correctly!')
        self.assertIsInstance(response['number_of_ae'], str, 'Home View: Number of AppEnsembles is not a string!')

        self.assertTrue(int(response['unique_triples']) > 0, 'Home View:Unique Triples are not initialized correctly!')
        self.assertIsInstance(response['unique_triples'], str, 'Home View: Number of Unique Triples is not a string!')

        self._standard_tests(response)


    def test_documentation_view(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        response = views.documentation_view(self, request)

        self._standard_tests(response)

    # TODO: view should be improved, because it is not dynamic. Afterwards improve this testing
    def test_documentation_docs_view(self):
        self.request.matchdict['document']= 'app-description_specification'
        response = views.documentation_docs_view(self.context, self.request)
        self._standard_tests(response)

    def test_documentation_docs_view_wrongparam(self):
        self.request.matchdict['wrongparam']= 'app-description_specification'
        self.assertRaises(KeyError,views.documentation_docs_view,self.context, self.request)

    def test_views_for_URIError(self):

        #tests wrong URIS for all the views with an request URI
        test_views=dict()
        test_views["AppEnsembleViews"]=list()
        test_views["AppPoolViews"]=list()

        test_views["AppEnsembleViews"].append({'view': "ae_details_view", 'ignore_test': []})
        test_views["AppEnsembleViews"].append({'view': "ae_visualize_bpm_view", 'ignore_test': []})
        test_views["AppEnsembleViews"].append({'view': "ae_get_bpmn_view", 'ignore_test': ["_tooMuchURI_butOK_test"]})
        test_views["AppEnsembleViews"].append({'view': "ae_get_ae_pkg_view", 'ignore_test': ["_tooMuchURI_butOK_test"]})

        test_views["AppPoolViews"].append({'view': "ap_app_details_view", 'ignore_test': ["_tooMuchURI_butOK_test","_wrongURI_test"]})

        for key in test_views:
            self.viewclass_to_test=key
            for x in test_views[key]:
                self._URI_error_tests(x['view'],x['ignore_test'])

        del(self.viewclass_to_test)

    # AppPool View tests

    def test_documentation_ap_pool_view(self):
        response = views.AppPoolViews.ap_pool_view(self)

        self._standard_tests(response)

        self.assertIsInstance(response['apps'], list)
        self.assertTrue(len(response['apps']) > 0)

        if (len(response['apps']) > 0):
            nameindex = ""
            for app in response['apps']:
                appname = app['name']
                # check the existence of attributes
                self.assertTrue(app['uri'] != None)
                self.assertTrue(appname != None)
                self.assertTrue(app['icon'] != None)
                self.assertTrue(app['binary'] != None)
                # Check the correct order
                self.assertTrue(appname > nameindex, "Applist is not ordered correctly")
                nameindex = appname


    def test_ap_app_details_view(self):
        self.request.params = MultiDict()
        self.request.params.add('URI', 'http://mustermann.de/maxApp')

        response = views.AppPoolViews(self.context, self.request).ap_app_details_view()
        self.assertEqual(response['details']['icon'],'http://mustermann.de/maxApp/res/icon.jpg')
        self._standard_tests(response)

    #TODO View seem to be broken. Check and adapt the test
    def test_api_ap_json_view(self):
        response = views.AppPoolViews(self.context, self.request).api_ap_json_view()
        self.assertTrue('json' in response)
        response=response['json']


    def test_zz_action_update_app_pool_view(self):
        self.request.registry.settings['app_pool_path']='aof:tests/res/test_pool.ttl'
        response = views.AppPoolViews(self.context, self.request).action_update_app_pool_view()
        self.assertIsInstance(response,Response)
        ap=AppPool.Instance()
        self.assertTrue(int(response.body)==ap.get_number_of_apps())

    # AppEnsemble Views

    def test_app_ensembles_view(self):
        response = views.AppEnsembleViews(self.context, self.request).app_ensembles_view()
        self._standard_tests(response)

    #TODO geht nicht mehr
    def test_ae_details_view(self):

        self.request.params = MultiDict()
        self.request.params.add('URI', 'testAppEnsemble')

        response = views.AppEnsembleViews(self.context, self.request).ae_details_view()
        self.assertEqual(response['ae_uri'], 'testAppEnsemble')
        #self.assertTrue(len(response['ae_apps']) > 1)

        self._standard_tests(response)

    def test_ae_visualize_bpm_view(self):
        self.request.params = MultiDict()
        self.request.params.add('URI', 'testAppEnsemble')

        response = views.AppEnsembleViews(self.context, self.request).ae_visualize_bpm_view()
        self.assertEqual(response['ae_uri'], 'testAppEnsemble')
        self.assertEqual(response['ae_has_bpmn'], True)
        self._standard_tests(response)

    def test_ae_get_bpmn_view(self):

        self.request.params = MultiDict()
        self.request.params.add('URI', 'testAppEnsemble')

        response = views.AppEnsembleViews(self.context, self.request).ae_get_bpmn_view()
        self.assertIsInstance(response,Response)
        self.assertEqual(response.headers.get('Content-Type'), 'txt/xml')
        self.assertTrue(int(response.headers.get('Content-Length'))<100)
        self.assertTrue(".bpmn" in response.headers.get('Content-Disposition'))

    #TODO geht nicht mehr
    def test_api_ae_json_view(self):
        response = views.AppEnsembleViews(self.context, self.request).api_ae_json_view()
        del(response['json']['5G-Demo'])
        self.assertTrue('json' in response)
        response=response['json']
        self.assertTrue('testAppEnsemble' in response)
        response=response['testAppEnsemble']
        self.assertEqual(response['uri'],'testAppEnsemble')
        #self.assertTrue(len(response['apps'])>1000)



    def test_ae_get_ae_pkg_view(self):
        self.request.params = MultiDict()
        self.request.params.add('URI', 'testAppEnsemble')

        response = views.AppEnsembleViews(self.context, self.request).ae_get_ae_pkg_view()
        self.assertIsInstance(response,FileResponse)
        self.assertEqual(response.headers.get('Content-Type'), 'application/vnd.aof.package-archive')
        self.assertTrue(".ae" in response.headers.get('Content-Disposition'))


    def test_zz_action_update_app_ensembles_view(self):
        response = views.AppEnsembleViews(self.context, self.request).action_update_app_ensembles_view()
        self.assertIsInstance(response,Response)
        aem=AppEnsembleManager.Instance()
        self.assertTrue(int(response.body)==len(aem))








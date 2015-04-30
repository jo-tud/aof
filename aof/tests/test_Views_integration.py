import unittest
from pyramid import testing

import aof.views as views
from pyramid.events import ApplicationCreated
from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool
from aof.tests.test_AppEnsemble import AppEnsembleTests
from aof.orchestration.AppEnsemble import AppEnsemble


class IntegrationViewTests(unittest.TestCase):


    def setUp(self):
        from pyramid.path import AssetResolver
        from aof.orchestration.AppPool import AppPool

        #import aof

        self.config = testing.setUp()
        #self.config.include('aof')

        a = AssetResolver()
        self.path = a.resolve('aof:tests/res/test_pool.ttl').abspath()
        self.ap=AppPool.Instance()
        self.ap.add_apps_from_app_pool_definition(source=self.path, format="turtle")


    def tearDown(self):
        testing.tearDown()

    def _meta_test(self,meta):
        self.assertIsInstance(meta['acronym'],str,'Home View: Meta-acronym is not a string!')
        self.assertTrue(len(meta['acronym'])>0,'Home View:Meta-acronym does not exist!')

        self.assertTrue(len(meta['appname'])>0,'Home View:Meta-appname does not exist!')
        self.assertIsInstance(meta['appname'],str,'Home View: meta-appname is not a string!')

    def _pagetitle_test(self,page_title):
        self.assertTrue(len(page_title)>0,'Page Title does not exist!')
        self.assertIsInstance(page_title,str,'Page Title is not a string!')


    def test_home_view(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        response = views.home_view(context,request)
        #print(response.status)
        self.assertTrue(int(response['number_of_apps'])>0,'Home View: AppPool is not initialized correctly!')
        self.assertIsInstance(response['number_of_apps'],str,'Home View: Number of Apps is not a string!')

        self.assertTrue(int(response['number_of_ae'])>0,'Home View:AppEnsembles are not initialized correctly!')
        self.assertIsInstance(response['number_of_ae'],str,'Home View: Number of AppEnsembles is not a string!')

        self.assertTrue(int(response['unique_triples'])>0,'Home View:Unique Triples are not initialized correctly!')
        self.assertIsInstance(response['unique_triples'],str,'Home View: Number of Unique Triples is not a string!')

        self._pagetitle_test(response['page_title'])
        self._meta_test(response['meta'])

    def test_documentation_view(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        response = views.documentation_view(self,request)

        self._pagetitle_test(response['page_title'])
        self._meta_test(response['meta'])

    #TODO
    """def test_documentation_docs_view(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        response = views.documentation_docs_view(context,request)

        self._pagetitle_test(response['page_title'])
        self._meta_test(response['meta'])
"""


    def test_documentation_ap_pool_view(self):
        response = views.AppPoolViews.ap_pool_view(self)

        self._pagetitle_test(response['page_title'])
        self._meta_test(response['meta'])

        self.assertIsInstance(response['apps'],list)
        self.assertTrue(len(response['apps'])>0)

        if(len(response['apps'])>0):
            nameindex=""
            for app in response['apps']:
                appname=app['name']
                # check the existence of attributes
                self.assertTrue(app['uri']!=None)
                self.assertTrue(appname!=None)
                self.assertTrue(app['icon']!=None)
                self.assertTrue(app['binary']!=None)
                # Check the correct order
                self.assertTrue(appname>nameindex,"Applist is not ordered correctly")
                nameindex=appname

    def test_ap_app_details_view(self):
        pass
    def test_api_ap_json_view(self):
        pass
    def test_action_update_app_pool_view(self):
        pass

    def test_app_ensembles_view(self):
        pass
    def test_ae_details_view(self):
        pass
    def test_ae_visualize_bpm_view(self):
        pass
    def test_ae_get_bpmn_view(self):
        pass
    def test_api_ae_json_view(self):
        pass
    def test_ae_get_ae_pkg_view(self):
        pass
    def test_action_update_app_ensembles_view(self):
        #response = views.AppEnsembleViews.action_update_app_ensembles_view(self)
        #print(response)
        pass






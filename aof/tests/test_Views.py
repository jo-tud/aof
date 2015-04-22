import unittest
from pyramid import testing

import aof.views as views
from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool
'''
class ViewTest_home_view(unittest.TestCase):

    # TODO: Make Integration Test work!
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

    def test_it(self):
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

        self.assertTrue(len(response['page_title'])>0,'Home View:Page Title does not exist!')
        self.assertIsInstance(response['page_title'],str,'Home View: Page Title is not a string!')

        self.assertIsInstance(response['meta']['acronym'],str,'Home View: Meta-acronym is not a string!')
        self.assertTrue(len(response['meta']['acronym'])>0,'Home View:Meta-acronym does not exist!')

        self.assertTrue(len(response['meta']['appname'])>0,'Home View:Meta-appname does not exist!')
        self.assertIsInstance(response['meta']['appname'],str,'Home View: meta-appname is not a string!')
'''

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        #import tempfile
        from aof import main
        #self.tmpdir = tempfile.mkdtemp()
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

        a = AssetResolver()
        path = a.resolve('aof:tests/res/test_pool.ttl').abspath()
        ap = AppPool.Instance()
        ap.add_apps_from_app_pool_definition(source=path, format="turtle")


    #def tearDown(self):
        #import shutil
        # shutil.rmtree( self.tmpdir )

    def test_root(self):
        res = self.testapp.get('/')
        self.assertEqual(res.charset,'UTF-8')
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.content_type,'text/html')
        #res. body
        #res.request.GET
        #print(res.request.GET)

    def test_not_existing_page(self):
        from webtest import AppError
        self.assertRaises(AppError,self.testapp.get,'/i-do-not-exist-test')

    def test_app_ensembles(self):
        self.assertEqual(self.testapp.get('/app-ensembles.html').status_code,200)

    #TODO: Load test-Appensemble
    def test_app_ensemble_details(self):
        #self.assertEqual(self.testapp.get('/').status_code,200)
        pass

    #TODO: Load test-Appensemble
    def test_app_ensemble_bpmn(self):
        #self.assertEqual(self.testapp.get('/').status_code,200)
        pass

    def test_app_pool(self):
        res=self.testapp.get('/app-pool.html')
        self.assertEqual(res.status_code,200)
        self.assertTrue(b'<title>App-Pool</title>' in res.body)

    def test_app_pool_details(self):
        res =self.testapp.get('/app-pool/details.html?URI=http://mustermann.de/maxApp')
        self.assertEqual(res.status_code,200)
        self.assertTrue(b'max@mustermann.de' in res.body)
        self.assertTrue(b'<title>App-Details</title>' in res.body)

    def test_app_pool_details_no_params(self):
        res =self.testapp.get('/app-pool/details.html')
        self.assertEqual(res.status_code,200)
        self.assertTrue(b'The parameter "URI" was not supplied' in res.body)

    def test_app_pool_details_no_uri_param(self):
        res =self.testapp.get('/app-pool/details.html?URI=')
        self.assertEqual(res.status_code,200)
        self.assertTrue(b'-parameter was empty' in res.body)

    def test_app_pool_details_wrong_uri_param(self):
        res =self.testapp.get('/app-pool/details.html?URI=http://abc')
        self.assertEqual(res.status_code,200)
        self.assertTrue(b'seem to be an Android App' in res.body)

    def test_documentation(self):
        self.assertEqual(self.testapp.get('/documentation.html').status_code,200)

    #TODO
    def test_documentation_docs(self):
        pass
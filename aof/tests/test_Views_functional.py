import unittest
from pyramid import testing

import aof.views as views
from pyramid.events import ApplicationCreated
from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool
from aof.tests.test_AppEnsemble import AppEnsembleTests


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from aof import main


        a = AssetResolver()
        path = a.resolve('aof:tests/res/test_pool.ttl').abspath()
        ap = AppPool.Instance()
        ap.add_apps_from_app_pool_definition(source=path, format="turtle")

        self.aeTests=AppEnsembleTests()
        self.aeTests._createTestArchive()


        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)




    def tearDown(self):
        self.aeTests._deleteTestArchive()

    def _status_code_test(self,testapp_get_result):
        self.assertEqual(testapp_get_result.status_code,200)

    def _body_title_test(self,res,title):
        self.assertTrue(bytes('<title>'+title+'</title>', 'utf-8') in res.body)

    def test_home_view(self):
        res = self.testapp.get('/')
        self.assertEqual(res.charset,'UTF-8')
        self._status_code_test(res)
        self.assertEqual(res.content_type,'text/html')
        self._body_title_test(res,"AOF Home")

    def test_not_existing_page(self):
        from webtest import AppError
        self.assertRaises(AppError,self.testapp.get,'/i-do-not-exist-test')

    def test_documentation(self):
        res=self.testapp.get('/documentation.html')
        self._status_code_test(res)
        self._body_title_test(res,"Documentation")

    def test_documentation_doc_exists(self):
        res =self.testapp.get('/doc/app-description_specification.html')
        self._status_code_test(res)
        self._body_title_test(res,"Documentation")

    # TODO: Documentation umschreiben
    def test_documentation_doc_not_exists(self):
        #res =self.testapp.get('/app-description_not_exists.html')
        #self._status_code_test(res)
        pass

    def test_app_ensembles(self):
        res=self.testapp.get('/app-ensembles.html')
        self._status_code_test(res)

    def test_app_ensemble_details(self):
        res=self.testapp.get('/app-ensembles/details.html?URI=testAppEnsemble')
        self._status_code_test(res)
        self.assertTrue(b'<h1>testAppEnsemble</h1>' in res.body)

    def test_app_ensemble_bpmn(self):
        res=self.testapp.get('/app-ensembles/visualize-bpm.html?URI=testAppEnsemble')
        self._status_code_test(res)
        self._body_title_test(res,"App-Ensemble Details")

    def test_app_pool(self):
        res=self.testapp.get('/app-pool.html')
        self._status_code_test(res)
        self._body_title_test(res,"App-Pool")

    def test_app_pool_details(self):
        res =self.testapp.get('/app-pool/details.html?URI=http://mustermann.de/maxApp')
        self._status_code_test(res)
        self._body_title_test(res,"App-Details")
        self.assertTrue(b'max@mustermann.de' in res.body)

    def test_app_pool_details_no_params(self):
        res =self.testapp.get('/app-pool/details.html')
        self._status_code_test(res)
        self.assertTrue(b'The parameter "URI" was not supplied' in res.body)

    def test_app_pool_details_no_uri_param(self):
        res =self.testapp.get('/app-pool/details.html?URI=')
        self._status_code_test(res)
        self.assertTrue(b'-parameter was empty' in res.body)

    def test_app_pool_details_wrong_uri_param(self):
        res =self.testapp.get('/app-pool/details.html?URI=http://abc')
        self._status_code_test(res)
        self.assertTrue(b'seem to be an Android App' in res.body)

import unittest
from pyramid import testing

from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool
from aof.orchestration.AppEnsembleManager import AppEnsembleManager
from aof.tests.test_AppEnsemble import AppEnsembleTests

import aof.tests



class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from aof import main

        # Setting up Testpool and TestAppEnsemble
        a = AssetResolver()
        path = a.resolve(aof.tests.settings["app_pool_path"]).abspath()
        ap = AppPool.Instance()
        ap.add_apps_from_app_pool_definition(source=path,format="turtle")

        self.aeTests=AppEnsembleTests()
        aof.tests._create_test_AppEnsemble()

        #Set up Test-HTML for Documentation
        aof.tests._create_test_html_file()

        # Creating app with parameter
        META=aof.tests.settings["META"]

        app = main({},app_pool_path=aof.tests.settings["app_pool_path"],
                    app_ensemble_folder=aof.tests.settings["app_ensemble_folder"],
                    documentation_docs_path=aof.tests.settings["documentation_docs_path"],
                    META=META)
        from webtest import TestApp
        self.testapp = TestApp(app)

        import ast
        self.meta=ast.literal_eval(META)


    def tearDown(self):
        aof.tests._delete_test_AppEnsemble()
        aof.tests._delete_test_html_file()

    def _status_code_test(self,testapp_get_result):
        self.assertEqual(testapp_get_result.status_code,200)

    def _body_title_test(self,res,title):
        self.assertTrue(bytes('<title>'+title+' - '+self.meta['acronym']+'</title>', 'utf-8') in res.body,"Title {} is not found in the document".format(title))

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
        res=self.testapp.get('/docs/index.html')
        self._status_code_test(res)
        self._body_title_test(res,"Documentation")

    def test_documentation_doc_exists(self):
        res =self.testapp.get('/docs/test.html')
        self._status_code_test(res)
        self.assertTrue(bytes('<testtag>HTML-Test</testtag>', 'utf-8') in res.body,"Test-Documentation Document} is not found")

    def test_documentation_doc_not_exists(self):
        from webtest import AppError
        self.assertRaises(AppError,self.testapp.get,'/docs/i-do-not-exist.html')

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
        self._body_title_test(res,"App-Ensemble Details | BPMN")

    def test_app_ensemble_update(self):
        aem=AppEnsembleManager.Instance()
        aem.pool.clear()
        num=len(aem)
        res =self.testapp.get('/api/actions/update-app-ensembles')
        self.assertGreater(int(res.body),num)

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
        from webtest import AppError
        self.assertRaises(AppError,self.testapp.get,'/app-pool/details.html?URI=http://abc')

    def test_app_pool_update(self):
        ap=AppPool.Instance()
        ap.clear_app_pool()
        num=ap.get_number_of_apps()
        res =self.testapp.get('/api/actions/update-app-pool')
        self.assertGreater(int(res.body),num)

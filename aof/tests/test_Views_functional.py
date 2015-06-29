import unittest
from pyramid import testing

from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool
from aof.orchestration.AppEnsemblePool import AppEnsemblePool
from aof.tests.test_AppEnsemble import AppEnsembleTests
from webtest import TestApp,TestRequest
import ast
from aof import main

import aof.tests



class FunctionalTests(unittest.TestCase):
    def setUp(self):


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

        self.testapp = TestApp(app)


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

    def test_app_ensemble_details_html(self):
        res=self.testapp.get('/app-ensembles/testAppEnsemble/details.html')
        self._status_code_test(res)
        self.assertTrue(b'<h1>testAppEnsemble</h1>' in res.body)

    def test_app_ensemble_bpmn(self):
        res=self.testapp.get('/app-ensembles/testAppEnsemble/bpm.html')
        self._status_code_test(res)
        self._body_title_test(res,"App-Ensemble Details | BPMN")

    def test_app_ensemble_update(self):
        aem=AppEnsemblePool.Instance()
        aem.pool.clear()
        num=len(aem)
        res =self.testapp.get('/api/actions/app-ensembles/update')
        self.assertGreater(int(res.body),num)

    def test_app_pool(self):
        res=self.testapp.get('/apps.html')
        self._status_code_test(res)
        self._body_title_test(res,"App-Pool")

    def test_app_pool_details(self):
        res =self.testapp.get('/apps/http%3A%2F%2Fmustermann.de%2FmaxApp/details.html', headers={"accept":'text/html'})
        self._status_code_test(res)
        self._body_title_test(res,"App-Details")
        self.assertTrue(b'max@mustermann.de' in res.body)

    def test_app_pool_details_no_uri_param(self):
        res =self.testapp.get('/apps//details.html')
        self._status_code_test(res)
        self.assertTrue(b'-parameter was empty' in res.body)

    def test_app_pool_details_wrong_uri_param(self):
        from webtest import AppError
        self.assertRaises(AppError,self.testapp.get,'/apps/URI%3Dhttp%3A%2F%2Fabc%2F/details.html')

    def test_app_pool_details_rdf(self):
        res = self.testapp.get('/apps/http%3A%2F%2Fmustermann.de%2FmaxApp/details.html', headers={"accept":'application/rdf+xml'})
        self._status_code_test(res)
        self.assertTrue(b'<rdf:RDF' in res.body)

    def test_app_pool_details_turtle(self):
        res = self.testapp.get('/apps/http%3A%2F%2Fmustermann.de%2FmaxApp/details.html', headers={"accept":'text/turtle'})
        self._status_code_test(res)
        self.assertTrue(b'@prefix' in res.body)

    def test_app_pool_update(self):
        ap=AppPool.Instance()
        ap.clear_app_pool()
        num=ap.get_number_of_apps()
        res =self.testapp.get('/api/actions/app-pool/update')
        self.assertGreater(int(res.body),num)

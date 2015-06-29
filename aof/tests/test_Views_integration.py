import unittest
from pyramid import testing
import json
import os

from aof.orchestration.AppEnsemblePool import AppEnsemblePool
from aof.orchestration.AppPool import AppPool
from webob.multidict import MultiDict
from pyramid.response import Response,FileResponse
from rdflib import URIRef,ConjunctiveGraph


from pyramid.httpexceptions import HTTPNotFound
from pyramid.path import AssetResolver
from aof.views.PageViews import PageViews
from aof.views.AppEnsembleViews import AppEnsembleViews
from aof.views.AppPoolViews import AppPoolViews,fill_graph_by_subject
from aof.views.DocumentationViews import DocumentationViews

import aof.tests
from aof.tests.test_AppEnsemble import AppEnsembleTests
from aof.orchestration.AppPool import AppPool





class IntegrationViewTests(unittest.TestCase):
    def setUp(self):

        self.config = testing.setUp(settings=aof.tests.settings)
        aof.tests._create_test_AppEnsemble()

        #Setting up Test-AppPool
        a = AssetResolver()
        self.path = a.resolve(aof.tests.settings["app_pool_path"]).abspath()
        self.ap = AppPool.Instance()
        self.ap.add_apps_from_app_pool_definition(source=self.path, format="turtle")

        #Setting up Test-AppEnsemble
        self.ae=AppEnsemblePool.Instance()
        self.ae.reload()

        #Setting up Test-HTML for Documentation
        aof.tests._create_test_html_file()

        # Setting up request and context
        self.request = testing.DummyRequest()
        self.context = testing.DummyResource()


    def tearDown(self):
        testing.tearDown()
        aof.tests._delete_test_AppEnsemble()
        aof.tests._delete_test_html_file()

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
        module = getattr(aof.views,self.viewclass_to_test)
        class_ = getattr(module, self.viewclass_to_test)
        ret=getattr(class_(self.context, self.request),self.view_to_test)()
        return ret

    def _noURI_test(self):
        response = self._call_view_to_test()
        self.assertTrue('not supplied' in response.text)
        self.assertTrue(int(response.headers.get('Content-Length')) < 500)

    def _emptyURI_test(self):
        self.request.params.add('URI', '')

        response = self._call_view_to_test()
        self.assertIsInstance(response, Response,"Error in "+self.view_to_test+"!")
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
        self.assertIsInstance(response, Response,"Error in "+self.view_to_test+"!")



    # General view tests

    def test_home_view(self):
        response = PageViews(self.context, self.request).page_home()

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
        response = DocumentationViews(self.context, self.request).page_overview()

        self._standard_tests(response)

    def test_documentation_docs_view(self):
        self.request.matchdict['document']= 'test.html'
        response = DocumentationViews(self.context, self.request).page_html_view()
        self._standard_tests(response)

    def test_documentation_docs_view_not_exist(self):
        self.request.matchdict['document']= 'i-do-not-exist.html'
        response = DocumentationViews(self.context, self.request).page_html_view()
        self.assertIsInstance(response,HTTPNotFound)

    def test_documentation_docs_view_wrongparam(self):
        self.request.matchdict['wrongparam']= 'app-description_specification.html'
        response=DocumentationViews(self.context, self.request)
        self.assertRaises(KeyError,response.page_html_view)

    def test_views_for_URIError(self):

        #tests wrong URIS for all the views with an request URI
        test_views=dict()
        test_views["AppEnsembleViews"]=list()
        test_views["AppPoolViews"]=list()

        test_views["AppEnsembleViews"].append({'view': "page_details", 'ignore_test': []})
        test_views["AppEnsembleViews"].append({'view': "page_visualize_bpm", 'ignore_test': []})
        test_views["AppEnsembleViews"].append({'view': "action_get_bpmn_data", 'ignore_test': ["_tooMuchURI_butOK_test"]})
        test_views["AppEnsembleViews"].append({'view': "action_get_ae_pkg", 'ignore_test': ["_tooMuchURI_butOK_test"]})

        test_views["AppPoolViews"].append({'view': "page_details", 'ignore_test': ["_tooMuchURI_butOK_test","_wrongURI_test"]})

        for key in test_views:
            self.viewclass_to_test=key
            for x in test_views[key]:
                self._URI_error_tests(x['view'],x['ignore_test'])

        del(self.viewclass_to_test)

    # AppPool View tests

    def test_documentation_ap_pool_view(self):
        response = AppPoolViews(self.context, self.request).page_overview()

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


    def test_ap_app_details_view_maxapp(self):
        self.request.params = MultiDict()
        self.request.params.add('URI', 'http://mustermann.de/maxApp')

        response = AppPoolViews(self.context, self.request).page_details()
        self.assertEqual(response['details']['icon'],'http://mustermann.de/maxApp/res/icon.jpg')
        self.assertIsNotNone(response['roles'])
        self.assertIsNotNone(response['creators'])
        self.assertIsNotNone(response['main_screenshot'])
        self.assertIsNotNone(response['screenshots'])
        self.assertIsNotNone(response['entry_points'])
        self.assertIsNotNone(response['exit_points'])
        self._standard_tests(response)

    def test_ap_app_details_view_minapp(self):
        self.request.params = MultiDict()
        self.request.params.add('URI', 'http://mustermann.de/minApp')

        response = AppPoolViews(self.context, self.request).page_details()
        self.assertIsNone(response['roles'])
        self.assertIsNone(response['creators'])
        self.assertIsNone(response['main_screenshot'])
        self.assertIsNone(response['screenshots'])
        self.assertIsNone(response['entry_points'])
        self.assertIsNone(response['exit_points'])
        self._standard_tests(response)


    def test_api_ap_json_view(self):
        response = AppPoolViews(self.context, self.request).api_json()
        self.assertTrue('MaxApp' in response)
        response=json.loads(response)['results']['bindings']
        self.assertTrue(response[0]['name']['value']==('MaxApp' or 'MinApp'))



    def test_zz_action_update_app_pool_view(self):
        self.request.registry.settings['app_pool_path']='aof:tests/res/test_pool.ttl'
        response = AppPoolViews(self.context, self.request).action_update()
        self.assertIsInstance(response,Response)
        ap=AppPool.Instance()
        self.assertTrue(int(response.body)==ap.get_number_of_apps())

    # AppEnsemble Views

    def test_app_ensembles_view(self):
        response = AppEnsembleViews(self.context, self.request).page_overview()
        self._standard_tests(response)


    def test_ae_details_view(self):

        self.request.params = MultiDict()
        self.request.params.add('URI', 'testAppEnsemble')

        response = AppEnsembleViews(self.context, self.request).page_details()
        self.assertEqual(response['ae_uri'], URIRef('testAppEnsemble'))

        self.assertTrue(len(response['ae_apps']) > 1)

        self._standard_tests(response)

    def test_ae_visualize_bpm_view(self):
        self.request.params = MultiDict()
        self.request.params.add('URI', 'testAppEnsemble')

        response = AppEnsembleViews(self.context, self.request).page_visualize_bpm()
        self.assertEqual(response['ae_uri'], URIRef('testAppEnsemble'))
        self.assertEqual(response['ae_has_bpmn'], True)
        self._standard_tests(response)

    def test_ae_get_bpmn_view(self):

        self.request.params = MultiDict()
        self.request.params.add('URI', 'testAppEnsemble')

        response = AppEnsembleViews(self.context, self.request).action_get_bpmn_data()
        self.assertIsInstance(response,Response)
        self.assertEqual(response.headers.get('Content-Type'), 'txt/xml')
        self.assertTrue(int(response.headers.get('Content-Length'))<100)
        self.assertTrue(".bpmn" in response.headers.get('Content-Disposition'))

    def test_api_ae_json_view(self):
        response = AppEnsembleViews(self.context, self.request).api_json()
        del(response['5G-Demo'])
        self.assertTrue('testAppEnsemble' in response)
        response=response['testAppEnsemble']
        self.assertEqual(response['uri'],'testAppEnsemble')
        self.assertTrue(len(response['apps'])>1000)



    def test_ae_get_ae_pkg_view(self):
        self.request.params = MultiDict()
        self.request.params.add('URI', 'testAppEnsemble')

        response = AppEnsembleViews(self.context, self.request).action_get_ae_pkg()
        self.assertIsInstance(response,FileResponse)
        self.assertEqual(response.headers.get('Content-Type'), 'application/vnd.aof.package-archive')
        self.assertTrue(".ae" in response.headers.get('Content-Disposition'))


    def test_zz_action_update_app_ensembles_view(self):
        response = AppEnsembleViews(self.context, self.request).action_update()
        self.assertIsInstance(response,Response)
        aem=AppEnsemblePool.Instance()
        self.assertTrue(int(response.body)==len(aem))



    def test_fill_graph_by_subject(self):
        """
        Tests whether the extracted graph contains all relevant statements about the URI.
        Must differ in 1 statement because in the max_test.ttl there is a dummy statement
        """
        originGraph = ConjunctiveGraph()
        originGraph.parse(source=AssetResolver().resolve("aof:tests/res/max_test.ttl").abspath(),format="turtle")
        newGraph = ConjunctiveGraph()
        newGraph=fill_graph_by_subject(originGraph, newGraph, URIRef("http://mustermann.de/maxApp"))

        diff=originGraph-newGraph
        self.assertIs(len(diff),1,"Method 'test_fill_graph_by_subject' extracts not all relevant Terms")

    def test_fill_graph_by_subject_wrongparams(self):
        newGraph = ConjunctiveGraph()
        res=fill_graph_by_subject("", newGraph, URIRef("http://mustermann.de/minApp"))
        self.assertTrue(isinstance(res,ConjunctiveGraph))
        self.assertTrue(len(res)==0)

        res=fill_graph_by_subject(self.ap, "", URIRef("http://mustermann.de/minApp"))
        self.assertTrue(isinstance(res,ConjunctiveGraph))
        self.assertTrue(len(res)>0)

        res=fill_graph_by_subject(self.ap, newGraph, "")
        self.assertTrue(res==self.ap)

        res=fill_graph_by_subject(self.ap, newGraph, 123)
        self.assertTrue(res==self.ap)

    def test_fill_graph_by_subject_too_much_iterations(self):

        newGraph = ConjunctiveGraph()
        res=fill_graph_by_subject(self.ap, newGraph, URIRef("http://mustermann.de/iteration7"))
        # Maximum 5 iterations are allowed = 2 base-statements + 5* 2 iteration-statements=12 statements
        self.assertIs(len(res),12)








__author__ = 'Korbi'
import unittest
import os
import zipfile
from xml.dom import minidom

import aof.tests
from pyramid import testing
from pyramid.path import AssetResolver
from aof.orchestration.AppEnsembleFactory import OrchestrationFactory,AppEnsembleFactory,GraphFactory,ZipFactory
from rdflib import URIRef, ConjunctiveGraph



class OrchestrationFactoryTests(unittest.TestCase):

    def setUp(self):
        # sets up the AppEnsemble Instance with an Testarchive
        self.config = testing.setUp(settings=aof.tests.settings)
        a = AssetResolver()
        #Path where the files for the zip are located
        bpmnpath=os.path.join(a.resolve(aof.tests.settings['test_resources_path']).abspath(),'testae.bpmn')
        with open(bpmnpath, 'r') as myfile:
            data=myfile.read()
        self.factory=OrchestrationFactory(data,'add')


    def tearDown(self):
        # Deletes the generated test archive
        testing.tearDown()

    def test_of_existence(self):
        self.assertIsInstance(self.factory,OrchestrationFactory)

    def test_of_attributes(self):
        self.assertNotEqual(self.factory.bpmn,"")
        self.assertIsInstance(self.factory.dom,minidom.Document)
        self.assertIsInstance(self.factory.appEnsembles["Participant_0sq20zh"],dict)

    def test_of_appEnsembles(self):
        self.assertTrue(len(self.factory.appEnsembles)==1)
        self.assertTrue("Participant_0sq20zh" in self.factory.appEnsembles.keys())
        ae=self.factory.appEnsembles["Participant_0sq20zh"]

        self.assertEqual(ae["participantName"],'Test-2')
        self.assertEqual(ae["processRef"],'Process_1')
        self.assertIsInstance(ae["dom"],minidom.Element)

class AppEnsembleFactoryTests(unittest.TestCase):

    def setUp(self):
        OrchestrationFactoryTests.setUp(self)
        self.factory=AppEnsembleFactory(self.factory.appEnsembles['Participant_0sq20zh'])

    def tearDown(self):
        # Deletes the generated test archive
        testing.tearDown()

    def test_factory(self):
        self.assertEqual(self.factory.name,"Test-2")  # TODO
        self.assertIsInstance(self.factory.dom,minidom.Element)

    def test_Warnings(self):
        self.assertEqual(self.factory.returnWarnings(),"")
        self.factory.registerWarning("test","test")
        self.factory.registerWarning("test2","test")
        self.factory.registerWarning("test","test2")
        self.assertDictEqual(self.factory.warnings,{"test":"test2","test2":"test"})

        self.assertIn("test",self.factory.returnWarnings())
        self.assertNotIn("nicht",self.factory.returnWarnings())

    # TODO
    def test_saveLog(self):
        pass

    def test_extractRequiredApps(self):
        self.assertTrue(len(self.factory.required_apps)==3)
        self.assertIsInstance(self.factory.required_apps[0],URIRef)

class GraphFactoryTests(unittest.TestCase):
    def setUp(self):
        AppEnsembleFactoryTests.setUp(self)
        self.factory=GraphFactory(self.factory)

    def tearDown(self):
        testing.tearDown()

    def test_factory(self):
        self.assertIsInstance(self.factory.g,ConjunctiveGraph)
        self.assertIsInstance(self.factory.factory,AppEnsembleFactory)

    # TODO
    def test_create(self):
        self.factory.create()

class ZipFactoryTest(unittest.TestCase):
    def setUp(self):
        AppEnsembleFactoryTests.setUp(self)
        self.factory=ZipFactory(self.factory)

    def tearDown(self):
        testing.tearDown()

    def test_downloadApps(self):
        self.assertTrue(len(self.factory.app_tmp_path)==0)




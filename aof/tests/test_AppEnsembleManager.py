import unittest
from pyramid import testing
from aof.orchestration.AppEnsembleManager import AppEnsembleManager
from aof.tests.test_AppEnsemble import AppEnsembleTests
from aof.orchestration.AppEnsemble import AppEnsemble
from pyramid.path import AssetResolver

class AppEnsembleManagerTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        # First add Testappensemble
        AppEnsembleTests._createTestArchive(self)
        # Load AppEnsembles
        self.aem=AppEnsembleManager.Instance()

    def tearDown(self):
        testing.tearDown()
        AppEnsembleTests._deleteTestArchive(self)

    def test_contains(self):
        self.assertTrue("testAppEnsemble" in self.aem)

    def test_contains_not(self):
        self.assertFalse("testAppEnsemble_NotExist" in self.aem)

    def test_len(self):
        self.assertGreaterEqual(len(self.aem),1)

    def test_getset_ae_folder_path(self):
        self.assertTrue(self.aem._ae_folder_path_backup!=None)
        self.assertTrue(self.aem._ae_folder_path_backup==self.aem._ae_folder_path)
        origin_path=self.aem._ae_folder_path_backup
        new_path='aof:tests/res/'
        self.aem.set_ae_folder_path(new_path)
        self.assertEqual(AssetResolver().resolve(new_path).abspath(),self.aem.get_ae_folder_path())
        self.aem.set_ae_folder_path(origin_path)

    #TODO KeyError wird nicht ausgelöst
    def test_hasget_AppEnsemble(self):
        self.assertFalse(self.aem.has_AppEnsemble("testAppEnsembleNotExist"))
        self.assertTrue(self.aem.has_AppEnsemble("testAppEnsemble"))

        #self.assertRaises(KeyError,self.aem.get_AppEnsemble,"testAppEnsembleNotExist")
        self.assertIsInstance(self.aem.get_AppEnsemble("testAppEnsemble"),AppEnsemble)
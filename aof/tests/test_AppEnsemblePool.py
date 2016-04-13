import unittest
from pyramid import testing
from aof.orchestration.AppEnsemblePool import AppEnsemblePool
from aof.tests.test_AppEnsemble import AppEnsembleTests
from aof.orchestration.AppEnsemble import AppEnsemble
from pyramid.path import AssetResolver
import aof.tests

class AppEnsembleManagerTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp(settings=aof.tests.settings)
        # First add Testappensemble
        aof.tests._create_test_AppEnsemble()
        # Load AppEnsembles
        self.aem=AppEnsemblePool.Instance()
        self.aem.reload()

    def tearDown(self):
        testing.tearDown()
        aof.tests._delete_test_AppEnsemble()

    def test_contains(self):
        self.assertTrue("testAppEnsemble" in self.aem)

    def test_str(self):
        string=str(self.aem)
        self.assertTrue("AppPoolManager-Details" in string)

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

    def test_hasget_AppEnsemble(self):
        self.assertFalse(self.aem.has_AppEnsemble("testAppEnsembleNotExist"))
        self.assertTrue(self.aem.has_AppEnsemble("testAppEnsemble"))

        self.assertIsNone(self.aem.get_AppEnsemble("testAppEnsembleNotExist"))
        self.assertIsInstance(self.aem.get_AppEnsemble("testAppEnsemble"),AppEnsemble)

    def test_get_all(self):
        pool=self.aem.get_all_AppEnsembles()
        self.assertTrue(isinstance(pool,dict))
        self.assertGreaterEqual(len(pool),1)

    def test_reload(self):
        originlen=len(self.aem)
        aof.tests._delete_test_AppEnsemble()
        self.aem.reload()
        newlen=len(self.aem)
        aof.tests._create_test_AppEnsemble()
        self.aem.reload()
        self.assertNotEqual(originlen,newlen)


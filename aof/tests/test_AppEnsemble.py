import unittest
import os
import zipfile

import aof.tests
from pyramid import testing
from pyramid.path import AssetResolver
from aof.orchestration.AppEnsemble import AppEnsemble



class AppEnsembleTests(unittest.TestCase):

    def setUp(self):
        # sets up the AppEnsemble Instance with an Testarchive
        self.config = testing.setUp(settings=aof.tests.settings)
        aof.tests._create_test_AppEnsemble()
        self.ae=AppEnsemble(aof.tests.settings['ae_name'])


    def tearDown(self):
        # Deletes the generated test archive
        testing.tearDown()
        aof.tests._delete_test_AppEnsemble()

    def test_hasget_bpm(self):
        self.assertTrue(self.ae.has_bpm())
        self.assertEqual(self.ae.get_bpm(),b'Test-BPMN')

    def test_hasget_file(self):
        self.assertTrue(self.ae.has_file('apps/max_test.ttl'))
        self.assertFalse(self.ae.has_file('apps/notexist.ttl'))
        self.assertNotEqual(self.ae.get_file('apps/max_test.ttl'),b'')
        self.assertRaises(IOError,self.ae.get_file,'apps/notexist.ttl')

    # TODO
    #def test_load_ae_model(self):
        # Don't know how to test!
        #self.ae.load_ae_model(self.destTestArchive + '/test_ae_empty.ttl')

    def test_getRequiredApps(self):
        # Tests if the amount of required apps is correct
        self.assertIs(len(self.ae.getRequiredApps().bindings),8,'Required Apps are not loaded properly')

    def test_delte_AppEnsemble(self):
        # Checks whether the AppEnsemble counter is decremented after deleting one
        count=AppEnsemble.counter-1
        self.ae.__del__()
        self.assertIs(count,AppEnsemble.counter,'AppEnsemble was not deleted properly')
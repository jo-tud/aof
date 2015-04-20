import unittest
import os
import zipfile

from pyramid import testing
from pyramid.path import AssetResolver
from aof.orchestration.AppEnsemble import AppEnsemble



class AppEnsembleTests(unittest.TestCase):

    def setUp(self):
        """
        creates an test archive with test-files and saves it into the App-Ensembles Folder and then sets up
        the AppEnsemble Instance
        """
        self.config = testing.setUp()
        self.a = AssetResolver()
        self.ae_name='testAppEnsemble'

        #Path where the files for the zip are located
        originsPath=self.a.resolve('aof:tests/res/').abspath()

        # Destination of the zip archive
        self.destTestArchive= self.a.resolve(AppEnsemble.ae_folder_path).abspath() + self.ae_name + AppEnsemble.ae_extension

        # Creation of the zip archive
        zip_ae = zipfile.ZipFile(self.destTestArchive, mode='w')
        try:
            zip_ae.write(originsPath + 'test_ae.ttl',AppEnsemble.ae_filename)
            zip_ae.write(originsPath + 'test_ae.bpmn',AppEnsemble.bpmn_filename)
            zip_ae.write(originsPath + 'max_test.ttl','apps/max_test.ttl')
            zip_ae.write(originsPath + 'min_test.ttl','apps/min_test.ttl')
        finally:
            zip_ae.close()

        # Set up the AppEnsemble
        self.ae=AppEnsemble(self.ae_name)

    def tearDown(self):
        # Deletes the generated test archive
        testing.tearDown()
        os.remove(self.destTestArchive)

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
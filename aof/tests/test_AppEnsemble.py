import unittest
import shutil
import os, sys
import zipfile


from pyramid import testing

from pyramid.path import AssetResolver
from aof.orchestration.AppEnsemble import AppEnsemble
from rdflib import URIRef

from aof.orchestration.namespaces import AOF, ANDROID

class AppEnsembleTests(unittest.TestCase):
    """

    TODO's:
    - make the test_ae.ttl work!
    - fix the AppEnsemble get_file error and make good error handling; apply testing
    - remove_app_ensemble doesn't work and is it good to remove the .ae file??
    """

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
        self.destTestArchive= self.a.resolve('aof:static/App-Ensembles/').abspath() + self.ae_name + '.ae'

        # Creation of the zip archive
        zip_ae = zipfile.ZipFile(self.destTestArchive, mode='w')
        try:
            zip_ae.write(originsPath + 'test_ae.ttl','aes.ttl')
            zip_ae.write(originsPath + 'test_ae.bpmn','ae.bpmn')
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

    def test_remove_app_ensemble(self):
        #
        pass

    def test_load_ae_model(self):
        #
        pass

    def test_remove_app_ensemble(self):
        #
        #self.ae.remove_app_ensemble()
        #os.remove(self.destTestArchive)
        #zip_ae = zipfile.ZipFile(self.destTestArchive, mode='r')
        pass

    def test_getRequiredApps(self):
        #
        pass
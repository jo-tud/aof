import unittest
import shutil
import os, sys

from pyramid import testing

from pyramid.path import AssetResolver
from aof.orchestration.AppEnsemble import AppEnsemble
from rdflib import URIRef

from aof.orchestration.namespaces import AOF, ANDROID

class AppEnsembleTests(unittest.TestCase):
    """

    TODO's:
    - copy archive and then to the tests and then delete the archive
    - pack the archive that it could be unpacked

    """

    def setUp(self):
        """
        Copies the test.ae archive into the App-Ensembles Folder and then sets up
        the Appensemble Instance
        """
        self.config = testing.setUp()
        self.a = AssetResolver()
        originTestArchive = self.a.resolve('aof:tests/res/').abspath() + "testAppEnsemble.ae"
        self.destTestArchive= self.a.resolve('aof:static/App-Ensembles/').abspath() + "testAppEnsemble.ae"
        #shutil.copyfile(originTestArchive, self.destTestArchive)
        #self.ae=AppEnsemble()


    def tearDown(self):
        testing.tearDown()
        #os.remove(self.destTestArchive)

    def test_test(self):
        pass
import unittest
import os
import aof.orchestration.ae_tools as ae_tools

from pyramid import testing
from pyramid.path import AssetResolver
from aof.orchestration.AppEnsemble import AppEnsemble

from aof.tests.test_AppEnsemble import AppEnsembleTests


"""
class ae_tools_Tests(AppEnsembleTests):

    def setUp(self):

        creates an test archive with test-files and saves it into the App-Ensembles Folder and then sets up
        the AppEnsemble Instance

        #Set the new AppEnsemble Folder to the test ressource folder
        AppEnsemble.ae_folder_path=AppEnsembleTests.ae_test_origin_path

        self.config = AppEnsembleTests.setUp(self)
        self.a = AssetResolver()

        # Creates an Test AppEnsemble with the standard ae_name from the test_AppEnsemble class
        AppEnsembleTests._createTestArchive(self)

        # Creates another Test AppEnsemble with another name
        AppEnsembleTests.ae_name='testAppEnsemble2'
        AppEnsembleTests._createTestArchive(self)
        # Set up the AppEnsemble
        AppEnsembleTests.ae_name='testAppEnsemble'

    # TODO: delete testAppEnsembles
    def tearDown(self):
        # Deletes the generated test archive
        testing.tearDown(self)
        AppEnsembleTests.ae_name='testAppEnsemble2'

    def test_getNumberOfAE(self):
        # Tests whether the amount of AEs in the Test folder is 2
        self.assertIs(ae_tools.getNumberOfAE(),2)

    def test_0_initializeExistingAE(self):
        # Is tested first
        aes=ae_tools.initializeExistingAE()
        list=[]
        for key in aes:
            list.append(key)
        list.sort()
        self.assertListEqual(list,['testAppEnsemble','testAppEnsemble2'],'AppEnsembles are not initialized properly')
"""
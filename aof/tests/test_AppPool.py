import unittest
from pyramid import testing

from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool
from rdflib import URIRef

class AppPoolTests(unittest.TestCase):
    """

    TODO's:
    - wie kann ich die entry_points addressieren
    """

    def setUp(self):
        # Sets up the AppPool for Testing with two apps (one with maximum attributes one with minimum attributes)
        self.config = testing.setUp()
        a = AssetResolver()
        self.path = a.resolve('aof:tests/res/test_pool.ttl').abspath()
        self.ap=AppPool.Instance(source=self.path, format="turtle")
        self.maxApp=URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor/LastSuccessfulBuild")
        self.minApp=URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AppEnsembleInstaller/")


    def tearDown(self):
        testing.tearDown()

    def test_0_get_number_of_apps(self):
        # Should be the first Test ("test_0_...").Tests whether the AppPool consists of two apps
        self.assertGreaterEqual(self.ap.get_number_of_apps(), 2, "Not all Apps where loaded in the AppPool!")
        self.assertLess(self.ap.get_number_of_apps(), 3, "The App which should be ignored (no installable artifact) was loaded too!")

    def test_clear_and_update_app_pool(self):
        # Clears AppPool and checks whether there are no items left. Then updates the AppPool with the test_pool.ttl and checks if there are two items again
        self.ap._clear_app_pool()
        self.assertIs(self.ap.get_number_of_apps(), 0, "AppPool's Clear-Method is broken!")

        self.ap.update_app_pool(source=self.path, format="turtle")
        self.assertIs(self.ap.get_number_of_apps(), 2, "AppPool's Update Method is broken!")


    def test_get_app_uris(self):
        # Tests the correct URIs of the two apps and tests whether both are in the AppPool.
        items=self.ap.get_app_uris()
        items.sort()
        for index, uri in enumerate(items, start=1):   # default is zero
            if index==1:
                self.assertEqual(str(uri),"http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor/LastSuccessfulBuild","The first AppUri in the AppPool isn't initialized correctly!")
            elif index==2:
                self.assertEqual(str(uri),"http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AppEnsembleInstaller/","The first AppUri in the AppPool isn't initialized correctly!")

        self.assertIs(self.ap.get_number_of_apps(), 2, "Number of Apps in the AppPool is not correct!")

    def test_get_name_maxminApp(self):
        # Tests if the App_labels are correct
        self.assertEqual(self.ap.get_name(self.maxApp),"AOF Conductor", 'Name of the "AOF Coductor" App is wrong!')
        self.assertEqual(self.ap.get_name(self.minApp),"ComVantage IAF Login App",'Name of the "ComVantage IAF Login App" App is wrong!')

    def test_get_description_maxminApp(self):
        # test if the description of the maxApp is correct and if the minApp has none.
        self.assertNotEqual(self.ap.get_description(self.maxApp),"","An App with an description returns NO description!")
        self.assertEqual(self.ap.get_description(self.minApp),"None","An App with NO description returns one!")

    def test_get_icon_uri_maxminApp(self):
        # test if the Icon Uri of the maxApp is correct and if the minApp has none.
        self.assertEqual(self.ap.get_icon_uri(self.maxApp),"www.testicon.de","An App with an Icon returns None!")
        self.assertEqual(self.ap.get_icon_uri(self.minApp),"None","An App with NO Icon returns one!")

    def test_get_binary_uri_maxApp(self):
        # test if the Binary uri of the maxApp is correct .
        self.assertEqual(self.ap.get_binary_uri(self.maxApp),"http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor/lastSuccessfulBuild/artifact/AppEnsembleInstaller/bin/AppEnsembleInstaller-release.apk","An App with an Binary Uri returns None!")

    def test_hasget_role_maxminApp(self):
        # Tests if the Roles are loaded correctly
        self.assertTrue(self.ap.has_role(self.maxApp),"App with a Role returns None!")
        self.assertFalse(self.ap.has_role(self.minApp),"App with no Role returns one!")

        maxRoles=self.ap.get_roles(self.maxApp)
        minRoles=self.ap.get_roles(self.minApp)

        self.assertListEqual(maxRoles,["http://eatld.et.tu-dresden.de/aof/Conductor"],"App roles were not correct loaded!")
        self.assertListEqual(minRoles,[],"App without roles seems to have some!")

    def test_is_android_app_maxminApp(self):
        self.assertTrue(self.ap.is_android_app(self.maxApp),"Conductor should be an Android App!")
        self.assertFalse(self.ap.is_android_app(self.minApp),"ComVantage IAF Login App (for the test case) should not be an Android App!")

    def test_hasget_main_screenshot_maxminApp(self):
        # Tests if the Main Screenshots are loaded correctly
        self.assertTrue(self.ap.has_main_screenshot(self.maxApp),"App with a Main Screenshot returns None!")
        self.assertFalse(self.ap.has_main_screenshot(self.minApp),"App with no Main Screenshot returns one!")

        maxScreenshots=self.ap.get_main_screenshot(self.maxApp)
        minScreenshots=self.ap.get_main_screenshot(self.minApp)

        self.assertDictEqual(maxScreenshots,{'comment': 'None', 'uri': 'http://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Full_score.jpg/320px-Full_score.jpg'},"App roles were not correct loaded!")
        self.assertDictEqual(minScreenshots,{'comment': 'None', 'uri': 'None'},"App without roles seems to have some!")

    def test_hasget_other_screenshot_maxminApp(self):
        # Tests if other Screenshots are loaded correctly
        self.assertTrue(self.ap.has_other_screenshots(self.maxApp),"App with another Screenshot returns None!")
        self.assertFalse(self.ap.has_other_screenshots(self.minApp),"App with no other Screenshot returns one!")

        maxScreenshots=self.ap.get_other_screenshots(self.maxApp)
        minScreenshots=self.ap.get_other_screenshots(self.minApp)

        self.assertIs(maxScreenshots.__len__(),2,"Number of other screenshots (Conductor app) is not correct")
        # checking the screenshots whether the one with the "main Screenshot"-Comment is in
        i=0
        while (i<maxScreenshots.__len__()):
            if maxScreenshots[i]['comment']=='Main Screenshot':
                break
            i+=1
        else:
            self.assertTrue(False,"The other Screenshots of the Conductor aren't loaded correctly")

        self.assertIs(minScreenshots.__len__(),0,"Number of other screenshots (ComVantage IAF Login App (for the test case)) is not correct")

    def test_hasget_creators_maxminApp(self):
        # Tests if the creators are loaded correctly
        self.assertTrue(self.ap.has_creator(self.maxApp),"App with Creators returns None!")
        self.assertFalse(self.ap.has_creator(self.minApp),"App with no Creators returns one!")

        maxCreators=self.ap.get_creators(self.maxApp)
        minCreators=self.ap.get_creators(self.minApp)

        self.assertIs(maxCreators.__len__(),1,"Number of Creators (Conductor app) is not correct")
        self.assertEqual(maxCreators[0]['name'],"Johannes Pfeffer")
        self.assertIs(minCreators.__len__(),0,"Number of Creators (ComVantage IAF Login App (for the test case)) is not correct")

    def test_hasget_entry_points_with_input_check_maxminApp(self):
        # Tests if the entry points are loaded correctly. Afterwards checks the Inputs for the Conductor entry point
        self.assertTrue(self.ap.has_entry_points(self.maxApp),"App with Creators returns None!")
        self.assertFalse(self.ap.has_entry_points(self.minApp),"App with no Creators returns one!")

        maxPoints=self.ap.get_entry_points(self.maxApp)
        minPoints=self.ap.get_entry_points(self.minApp)

        self.assertIs(maxPoints.__len__(),2,"Number of Creators (Conductor app) is not correct")

        # Searching the right Entry Point of the maxApp for the validation of its content. If it is not found give out an error
        i=0
        while (i<maxPoints.__len__()):
            if maxPoints[i]['android_name']=='org.aof.action.START_WORKFLOW':
                entryPoint=maxPoints[i]
                break
            i+=1
        else:
            self.assertTrue(False,"The Entry Points of the Conductor aren't loaded correctly")
        # validation of the content
        self.assertEqual(entryPoint['label'],"Start Workflow")

        self.assertIs(minPoints.__len__(),0,"Number of Creators (ComVantage IAF Login App (for the test case)) is not correct")

        # Checking the inputs of the entrypoint which is checked

        # Don't know how to call the input???

    def test_hasget_exit_points_with_output_check_maxminApp(self):
        # Tests if the exit points are loaded correctly. Afterwards checks the Outputs for the Conductor exit point
        pass
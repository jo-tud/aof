import unittest
from pyramid import testing

from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool
from rdflib import URIRef
from rdflib.term import Literal
from aof.orchestration.namespaces import AOF, ANDROID
import aof.tests


class AppPoolTests(unittest.TestCase):

    def setUp(self):
        # Sets up the AppPool for Testing with two apps (one with maximum attributes one with minimum attributes)
        self.config = testing.setUp(settings=aof.tests.settings)
        a = AssetResolver()
        self.path = a.resolve(aof.tests.settings["app_pool_path"]).abspath()
        self.ap=AppPool.Instance()
        self.ap.add_apps_from_app_pool_definition(source=self.path, format="turtle")
        self.maxApp=URIRef("http://mustermann.de/maxApp")
        self.minApp=URIRef("http://mustermann.de/minApp")

    def tearDown(self):
        testing.tearDown()

    def test_0_get_number_of_apps(self):
        # Should be the first Test ("test_0_...").Tests whether the AppPool consists of two apps
        self.assertGreaterEqual(self.ap.get_number_of_apps(), 2, "Not all Apps where loaded in the AppPool!")
        self.assertLess(self.ap.get_number_of_apps(), 3, "The App which should be ignored (no installable artifact) was loaded too!")

    def test_clear_and_update_app_pool(self):
        # Clears AppPool and checks whether there are no items left. Then updates the AppPool with the test_pool.ttl and checks if there are two items again
        self.ap.clear_app_pool()
        self.assertIs(self.ap.get_number_of_apps(), 0, "AppPool's Clear-Method is broken!")

        self.ap.add_apps_from_app_pool_definition(source=self.path, format="turtle")
        self.assertIs(self.ap.get_number_of_apps(), 2, "AppPool's Update Method is broken!")


    def test_get_app_uris(self):
        # Tests the correct URIs of the two apps and tests whether both are in the AppPool.
        items=self.ap.get_app_uris()
        items.sort()
        for index, uri in enumerate(items, start=1):   # default is zero
            if index==1:
                self.assertEqual(str(uri),"http://mustermann.de/maxApp","The first AppUri in the AppPool isn't initialized correctly!")
            elif index==2:
                self.assertEqual(str(uri),"http://mustermann.de/minApp","The first AppUri in the AppPool isn't initialized correctly!")

        self.assertIs(self.ap.get_number_of_apps(), 2, "Number of Apps in the AppPool is not correct!")

    def test_get_name_maxminApp(self):
        # Tests if the App_labels are correct
        self.assertEqual(self.ap.get_name(self.maxApp),"MaxApp", 'Name of the "MaxApp" is wrong!')
        self.assertEqual(self.ap.get_name(self.minApp),"MinApp",'Name of the "MinApp" is wrong!')

    def test_get_description_maxminApp(self):
        # test if the description of the maxApp is correct and if the minApp has none.
        self.assertNotEqual(self.ap.get_description(self.maxApp),"","An App with an description returns NO description!")
        self.assertEqual(self.ap.get_description(self.minApp),"None","An App with NO description returns one!")

    def test_get_icon_uri_maxminApp(self):
        # test if the Icon Uri of the maxApp is correct and if the minApp has none.
        self.assertEqual(str(self.ap.get_icon_uri(self.maxApp)),"http://mustermann.de/maxApp/res/icon.jpg","An App with an Icon returns None!")
        self.assertEqual(str(self.ap.get_icon_uri(self.minApp)),"None","An App with NO Icon returns one!")

    def test_get_install_uri_maxApp(self):
        # test if the Binary uri of the maxApp is correct .
        self.assertEqual(self.ap.get_install_uri(self.maxApp),"http://mustermann.de/maxApp/res/install.apk","An App with an Binary Uri returns None!")

    def test_hasget_role_maxminApp(self):
        # Tests if the Roles are loaded correctly
        self.assertTrue(self.ap.has_role(self.maxApp),"App with a Role returns None!")
        self.assertFalse(self.ap.has_role(self.minApp),"App with no Role returns one!")

        maxRoles=self.ap.get_roles(self.maxApp)
        minRoles=self.ap.get_roles(self.minApp)

        self.assertListEqual(maxRoles,["http://eatld.et.tu-dresden.de/aof/Conductor"],"App roles were not correct loaded!")
        self.assertListEqual(minRoles,[],"App without roles seems to have some!")

    def test_is_android_app_maxminApp(self):
        self.assertTrue(self.ap.is_android_app(self.maxApp),"MapApp should be an Android App!")
        self.assertTrue(self.ap.is_android_app(self.minApp),"MinApp should not be an Android App!")


    def test_hasget_main_screenshot_maxminApp(self):
        # Tests if the Main Screenshots are loaded correctly
        self.assertTrue(self.ap.has_main_screenshot(self.maxApp),"App with a Main Screenshot returns None!")
        self.assertFalse(self.ap.has_main_screenshot(self.minApp),"App with no Main Screenshot returns one!")

        maxScreenshots=self.ap.get_main_screenshot(self.maxApp)
        minScreenshots=self.ap.get_main_screenshot(self.minApp)

        self.assertDictEqual(maxScreenshots,{'comment': 'None', 'uri': 'http://mustermann.de/maxApp/res/mainScreenshot.jpg'},"App roles were not correct loaded!")
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
            self.assertTrue(False,"The other Screenshots of the MaxApp aren't loaded correctly")

        self.assertIs(minScreenshots.__len__(),0,"Number of other screenshots (MinApp) is not correct")

    def test_hasget_creators_maxminApp(self):
        # Tests if the creators are loaded correctly
        self.assertTrue(self.ap.has_creator(self.maxApp),"App with Creators returns None!")
        self.assertFalse(self.ap.has_creator(self.minApp),"App with no Creators returns one!")

        maxCreators=self.ap.get_creators(self.maxApp)
        minCreators=self.ap.get_creators(self.minApp)

        self.assertIs(maxCreators.__len__(),1,"Number of Creators (MaxApp) is not correct")
        self.assertEqual(maxCreators[0]['name'],"Mustermann")
        self.assertIs(minCreators.__len__(),0,"Number of Creators (MinApp) is not correct")

    def test_hasget_entry_points_with_input_check_maxminApp(self):
        # Tests if the entry points are loaded correctly. Afterwards checks the Inputs for the Conductor entry point
        self.assertTrue(self.ap.has_entry_points(self.maxApp),"App with Creators returns None!")
        self.assertFalse(self.ap.has_entry_points(self.minApp),"App with no Creators returns one!")

        maxPoints=self.ap.get_entry_points(self.maxApp)
        minPoints=self.ap.get_entry_points(self.minApp)

        self.assertIs(maxPoints.__len__(),2,"Number of EntryPoints (MaxApp) is not correct")

        # Searching the right Entry Point of the maxApp for the validation of its content. If it is not found give out an error
        i=0
        while (i<maxPoints.__len__()):
            if maxPoints[i]['android_name']=='org.aof.action.START_WORKFLOW':
                entryPoint=maxPoints[i]
                break
            i+=1
        else:
            self.assertTrue(False,"The Entry Points of the MaxApp aren't loaded correctly")

        # validation of the content
        self.assertEqual(entryPoint['label'],"Start Workflow")

        self.assertIs(entryPoint['inputs'].__len__(),2,"The Number if EntryPoint inputs is not correct!")
        i=0
        while (i<entryPoint['inputs'].__len__()):
            if entryPoint['inputs'][i]['comment']=='**Testkommentar**':
                break
            i+=1
        else:
            self.assertTrue(False,"The Entry Points Inputs of the MaxApp aren't loaded correctly")

        self.assertIs(minPoints.__len__(),0,"Number of EntryPoints (MinApp) is not correct")

    def test_hasget_exit_points_with_output_check_maxminApp(self):
        # Tests if the exit points are loaded correctly. Afterwards checks the Outputs for the Conductor exit point
        self.assertTrue(self.ap.has_exit_points(self.maxApp),"App with Creators returns None!")
        self.assertFalse(self.ap.has_exit_points(self.minApp),"App with no Creators returns one!")

        maxPoints=self.ap.get_exit_points(self.maxApp)
        minPoints=self.ap.get_exit_points(self.minApp)

        self.assertIs(maxPoints.__len__(),1,"Number of exitPoints (MaxApp) is not correct")

        # Searching the right exit Point of the maxApp for the validation of its content. If it is not found give out an error
        i=0
        while (i<maxPoints.__len__()):
            if maxPoints[i]['label']=='Main_exit_point':
                exitPoint=maxPoints[i]
                break
            i+=1
        else:
            self.assertTrue(False,"The exit Points of the MaxApp aren't loaded correctly")

        # validation of the content
        self.assertEqual(exitPoint['comment'],"DescriptionExitPoint")

        self.assertIs(exitPoint['outputs'].__len__(),1,"The Number if exitPoint outputs is not correct!")
        i=0
        while (i<exitPoint['outputs'].__len__()):
            if exitPoint['outputs'][i]['has_datatype']=='http://www.w3.org/2001/XMLSchema#anyURI':
                break
            i+=1
        else:
            self.assertTrue(False,"The exit Points outputs of the MaxApp aren't loaded correctly")

        self.assertIs(minPoints.__len__(),0,"Number of Creators (MinApp) is not correct")

    def test_buildNumber_all(self):
        # prepare
        has_v=list()
        v=list()
        for o in self.ap.objects(self.maxApp, AOF.hasVersion ):
            has_v.append((self.maxApp, AOF.hasVersion,o) )
        for o in self.ap.objects(self.maxApp, AOF.version ):
            v.append((self.maxApp, AOF.version,o))
        has_v=has_v[0]
        v=v[0]
        self.ap.remove(has_v)
        self.ap.remove(v)

        # AOF.hasVersion:no - AOF.version:no
        result= self.ap.get_build_number(self.maxApp)
        self.assertEqual("N/A",result)

        # AOF.hasVersion:no - AOF.version:yes
        self.ap.add(v)
        result= self.ap.get_build_number(self.maxApp)
        self.assertEqual(Literal(1),result)

        # AOF.hasVersion:yes - AOF.version:yes
        self.ap.add(has_v)
        result= self.ap.get_build_number(self.maxApp)
        self.assertTrue("(1)" in result)

        # AOF.hasVersion:yes - AOF.version:no
        self.ap.remove(v)
        result= self.ap.get_build_number(self.maxApp)
        self.assertTrue("(1)"  not in result and "N/A" not in result)

        # AOF.hasVersion:yes but INVALID URI - AOF.version:no
        self.ap.remove(has_v)
        has_v_wrong=(self.maxApp, AOF.hasVersion,URIRef("httptest:test.test/test"))
        self.ap.add(has_v_wrong)
        result= self.ap.get_build_number(self.maxApp)
        self.assertEqual("N/A",result)

        #clear
        self.ap.remove(has_v_wrong)
        self.ap.add(v)
        self.ap.add(has_v)

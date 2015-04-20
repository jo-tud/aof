import unittest
from pyramid import testing

from aof.orchestration.Singleton import Singleton


@Singleton
class DummyClass():
    # Dummy Class with parameters for testing the singleton
    arg1 = ""
    arg2 = ""
    arg3 = ""

    def __init__(self):
       pass

    def setArg(self, arg1,arg2,arg3):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

class SingletonTests(unittest.TestCase):
    """ Class for testing the Singleton-Functionality with an Dummy Class. Testing includes:
        - Initialitation with parameters
        - Multiexistence of Singletons
        - Callability without the Instance()-Funktion
        - Correctness of the __instancecheck__
        To do:
        - the correct reinitialization of the Singleton (Params should be renewed)
        - Initialitation without and with parameters
    """

    def setUp(self):
        self.config = testing.setUp()


    def tearDown(self):
        testing.tearDown()

    def test_singleton_withparam_established(self):
        # Set up a Singleton with Parameters and test for existence and correct initialization for each parameter
        dict = {"house": "Haus", "cat": "Katze", "black": "schwarz"}
        inst = DummyClass.Instance()
        inst.setArg("Dummyparameter", 10, dict)
        self.assertIsInstance(inst, DummyClass, "Dummy Singleton with Parameter was not established!")
        self.assertIs(inst.arg1, "Dummyparameter")
        self.assertIs(inst.arg2, 10)
        self.assertIs(inst.arg3["house"], "Haus")
        self.assertIs(len(inst.arg3),3)
        self.assertIsNot(len(inst.arg3),2)
        self.assertIsNot(inst.arg2,None)

    def test_singleton_noparam_established(self):
        # Set up a Singleton and test for existence
        entity=DummyClass.Instance()
        self.assertIsInstance(entity,DummyClass,"Dummy Singleton with no Parameter was not established!")



    def test_singleton_multiexistence(self):
        # Tests whether there is really only one instance of the Singleton
        inst1 = DummyClass.Instance()
        inst2 = DummyClass.Instance()
        self.assertEqual(inst1, inst2, "There are multiple instances of a Singleton!")


    def test_call_without_Instance(self):
        # Tests whether the Singleton could called without Instance()
        self.assertRaises(TypeError, DummyClass)

    def test_call_with_Instance_and_parameter(self):
        # Tests whether the Singleton could called without Instance()
        self.assertRaises(TypeError, DummyClass.Instance,"abd",10)

    def test_instancecheck(self):
        # Tests if the inctancecheck works proper
        inst = DummyClass.Instance()
        self.assertTrue(DummyClass.__instancecheck__(inst))


    def test_modify_parameters(self):
        # Tests if the the Instance of Singleton could be reinitialized
        inst=DummyClass.Instance()
        inst.setArg("Dummyparameter",10,{"apple":"fruit"})
        self.assertIs(inst.arg1,"Dummyparameter")
        self.assertIs(inst.arg2,10)
        self.assertIs(inst.arg3["apple"],"fruit")
        inst.setArg(None,None,None)
        self.assertIs(inst.arg1,None)
        self.assertIs(inst.arg2,None)
        self.assertIs(inst.arg3,None)

import unittest
from pyramid import testing

from pyramid.path import AssetResolver
from aof.orchestration.AppPool import AppPool



class AppPoolTests(unittest.TestCase):
    """
    """
    def setUp(self):
        self.config = testing.setUp()
#        a = AssetResolver()
#        path = a.resolve('aof:tests/res/test_pool.ttl').abspath()
#        AppPool.Instance(source=path,format="turtle")

    def tearDown(self):
        testing.tearDown()

    def test_get_number_of_apps(self):
#        ap=AppPool.Instance()
#       self.assertIs(ap.get_number_of_apps, 2,"Number of Apps in the AppPool is not correct!")
        pass
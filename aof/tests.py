import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_home_view(self):
        from .views import home_view
        request = testing.DummyRequest()
        info = home_view(request)
        self.assertEqual(info['page_title'], 'Home')

    def test_demo_apps_view(self):
        from .views import demo_apps_view
        request = testing.DummyRequest()
        info = demo_apps_view(request)
        self.assertTrue(type(info['apps']) == list)

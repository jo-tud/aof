import unittest
from aof.tools.AOFGraph import AOFGraph, AOF
from aof.tools.AppPool import AppPool
from rdflib import Dataset, Graph, URIRef
from rdflib.plugins.memory import IOMemory


from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()


class ToolsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_aof_graph(self):
        self.assertRaises(TypeError, AOFGraph)
        g = AOFGraph.Instance()
        self.assertIsInstance(g, Dataset)
        self.assertIsInstance(g.store, IOMemory)
        self.assertEquals(g.__len__(),0)
        self.assertEquals(AOF, URIRef('http://eatld.et.tu-dresden.de/aof/'))

    def test_app_pool(self):
        uri = "http://#"
        ctxt = URIRef('http://eatld.et.tu-dresden.de/aof/AppPool')

        self.assertRaises(TypeError, AOFGraph)

        ap = AppPool.Instance(uri)
        self.assertEquals(ap.init_data_URI, uri)
        self.assertIsInstance(ap, Graph)
        self.assertIsInstance(ap.store, IOMemory)

        # Make sure ap is really a part of g
        g = AOFGraph.Instance()
        self.assertEquals(ap.identifier, ctxt)
        self.assertEquals(ap.store, g.store)
        self.assertEquals(ap, g.graph(ctxt))
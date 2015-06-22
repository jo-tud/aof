import unittest
from pyramid import testing
from aof.orchestration.AOFPool import AOFPool
from rdflib import URIRef

import aof.tests

class AOFPool_Test(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings=aof.tests.settings)
        self.maxApp=URIRef("http://mustermann.de/maxApp")
        self.minApp=URIRef("http://mustermann.de/minApp")

    def tearDown(self):
        testing.tearDown()


    def test_QRCode_generate_valid(self):
        response=AOFPool().get_QRCode("http://mustermann.de/minApp")
        self.assertEqual("/tmp/qrcodes/6545b7b29202cbb09883dd0b4595a149.svg",response)

    def test_QRCode_generate_notvalid(self):
        response=AOFPool().get_QRCode("http://mustermann.de/maxApp")
        self.assertNotEqual("/tmp/qrcodes/6545b7b29202cbb09883dd0b4595a149.svg",response)

    def test_QRCode_generate_wrongURI(self):
        response=AOFPool().get_QRCode("mustermann.de/maxApp")
        self.assertIsNone(response)
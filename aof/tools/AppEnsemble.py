from rdflib import Graph, util
from pyramid.path import AssetResolver
from aof.tools.AOFGraph import AOFGraph, AOF
from aof.tools.Singleton import Singleton

import os # os abstraction (e.g. listdir)
import logging
# This class should accept a turtle file or a zip file
class AppEnsemble(Graph):
    counter = 0
    def __init__(self, ae_desc):
        type(self).counter += 1
        g = AOFGraph.Instance()
        self.id = "http://eatld.et.tu-dresden.de/aof/" + str(1)
        self.log = logging.getLogger(__name__)
        self.ae_desc = ae_desc

        Graph.__init__(self, store=g.store)

        a = AssetResolver()
        ae_path = a.resolve('aof:static/App-Ensembles/').abspath() + self.identifier + ".ae"
        self.ae_file = open(ae_path, 'w')

        def loadAEDescription(self):
            try:
                self.parse(self.ae_desc, format=util.guess_format(self.ae_desc)) #TODO: Catch parsing errors
            except:
                self.log.error("There was a problem parsing" %self.ae)

        loadAEDescription(self)

    @classmethod
    def from_zip(cls):
        return cls(random(100))

    @classmethod
    def from_ttl(cls):
        return cls(random(33))

    def __del__(self):
        type(self).counter -= 1
        self.ae_file.close()
        #os.remove(self.ae_file.name)


    def addApps(self,apps):
        for app in apps:
            pass

    def remove_AppEnsemble(self):
        self.ae_file.close()
        os.remove(self.ae_file.name)
        del(self)


# Will only be called when executed from shell
if __name__ == "__main__":
    ae= AppEnsemble()
    print("Instance number: %i" % ae.counter)
    print(ae.identifier)

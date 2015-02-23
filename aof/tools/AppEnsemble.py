from rdflib import Graph, util
from pyramid.path import AssetResolver
from aof.tools.AOFGraph import AOFGraph
from aof.tools.namespaces import AOF
from aof.tools.Singleton import Singleton
import zipfile
import fnmatch

import os # os abstraction (e.g. listdir)
import logging

__all__ = [
    'AppEnsemble'
]
# This class should accept a turtle file or a zip file
class AppEnsemble(Graph):
    counter = 0
    def __init__(self,identifier=None):
        type(self).counter += 1
        g = AOFGraph.Instance()
        self.log = logging.getLogger(__name__)
        self.a = AssetResolver()

        # If an identifier is given it is used as a graph identifier
        # If a file IDENTIFIER.ae is found in the standard path it is read and used
        if identifier:
            assert isinstance(identifier, str)
            id = identifier
            Graph.__init__(self, store=g.store, identifier=id)
            self.ae_pkg_path = self.a.resolve('aof:static/App-Ensembles/' + identifier + '.ae').abspath()

            if os.path.isfile(self.ae_pkg_path):
                with zipfile.ZipFile(self.ae_pkg_path, "r") as ae_pkg:
                    for name in ae_pkg.namelist():
                        if fnmatch.fnmatch(name, 'ae.*'):
                            ae_model = ae_pkg.read('ae.ttl').decode()
                            self.parse(data=ae_model, format=util.guess_format(name))

        else:
            Graph.__init__(self, store=g.store)
            self.ae_pkg_path = self.a.resolve('aof:static/App-Ensembles/').abspath() + self.identifier + ".ae"
            zipfile.ZipFile(self.ae_pkg_path, 'w')

    def __del__(self):
        type(self).counter -= 1
        #os.remove(self.ae_file.name)


    def addApps(self,apps):
        for app in apps:
            pass

    # Wrapper for self.parse
    def loadAEModel(self,source):
        self.parse(source)

    def remove_AppEnsemble(self):
        os.remove(self.ae_file.name)
        del(self)


# Will only be called when executed from shell
if __name__ == "__main__":
    ae= AppEnsemble()
    print("Instance number: %i" % ae.counter)
    print(ae.identifier)

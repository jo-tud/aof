from rdflib import Graph, util
from pyramid.path import AssetResolver
from aof.orchestration.AOFGraph import AOFGraph
from aof.orchestration.namespaces import AOF
from aof.orchestration.Singleton import Singleton
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
                        if fnmatch.fnmatch(name, 'ae.ttl'):
                            ae_model = ae_pkg.read('ae.ttl').decode()
                            self.parse(data=ae_model, format=util.guess_format(name))
                    ae_pkg.close()

        else:
            Graph.__init__(self, store=g.store)
            self.ae_pkg_path = self.a.resolve('aof:static/App-Ensembles/').abspath() + self.identifier + ".ae"
            zipfile.ZipFile(self.ae_pkg_path, 'w')

    def __del__(self):
        type(self).counter -= 1
        #os.remove(self.ae_file.name)

    # TODO
    def add_apps(self,apps):
        for app in apps:
            pass

    # Wrapper for self.parse
    def load_ae_model(self,source):
        self.parse(source)

    def remove_app_ensemble(self):
        os.remove(self.ae_file.name)
        del(self)

    def has_bpm(self):
        return self.has_file('ae.bpmn')

    def get_bpm(self):
        return self.get_file('ae.bpmn')

    def has_file(self,filename):
        with zipfile.ZipFile(self.ae_pkg_path, "r") as ae_pkg:
            if filename in ae_pkg.namelist():
                return True
            else:
                return False


    def get_file(self, filename):
        with zipfile.ZipFile(self.ae_pkg_path, "r") as ae_pkg:
            for name in ae_pkg.namelist():
                if fnmatch.fnmatch(name, filename):
                    file = ae_pkg.read(filename)
                    ae_pkg.close()
                    return file
                else:
                    return 'File "%s" not found' % filename
                    #TODO: Raise an appropriate error

    def getRequiredApps(self):
        #TODO: Adapt to new ontology
        res = self.query("""
            PREFIX o: <http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#>
            SELECT DISTINCT ?app_uri ?name
            WHERE {
                [] o:instanceOf ?app_uri;
                   o:Name ?name .
            }
        """)
        return res

# Will only be called when executed from shell
if __name__ == "__main__":
    ae= AppEnsemble('5G-Demo')
    print("Instance number: %i" % ae.counter)
    print(ae.identifier)
    test = ae.getRequiredApps()
    print(test)

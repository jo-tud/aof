from rdflib import Graph, util, URIRef, Namespace, RDF, RDFS
from pyramid.path import AssetResolver
from aof.orchestration.namespaces import AOF, BPMN2
import zipfile
import fnmatch
from rdflib.plugins.memory import IOMemory
import os # os abstraction (e.g. listdir)
import logging

__all__ = [
    'AppEnsemble'
]

_ae_folder_path='aof:resources/App-Ensembles/'

# This class should accept a turtle file or a zip file
class AppEnsemble(Graph):
    counter = 0
    ae_extension='.ae'
    ae_filename = 'ae.ttl'
    bpmn_filename= 'ae.bpmn'
    ae_folder_path=_ae_folder_path

    def __init__(self,identifier=None):
        #AOFGraph.__init__(self)
        type(self).counter += 1
        self.log = logging.getLogger(__name__)
        self.a = AssetResolver()

        # If an identifier is given it is used as a graph identifier
        # If a file IDENTIFIER.ae is found in the standard path it is read and used
        if identifier:
            assert isinstance(identifier, str)
            id = identifier
            store = IOMemory()
            Graph.__init__(self, store=store, identifier=id)
            self.ae_pkg_path = self.a.resolve(_ae_folder_path + identifier + self.ae_extension).abspath()

            if os.path.isfile(self.ae_pkg_path):
                with zipfile.ZipFile(self.ae_pkg_path, "r") as ae_pkg:
                    for name in ae_pkg.namelist():
                        if fnmatch.fnmatch(name, self.ae_filename):
                            ae_model = ae_pkg.read(self.ae_filename).decode()
                            self.parse(data=ae_model, format=util.guess_format(name))
                    ae_pkg.close()

        else:
            Graph.__init__(self, store=g.store)
            self.ae_pkg_path = self.a.resolve(_ae_folder_path).abspath() + self.identifier + self.ae_extension
            zipfile.ZipFile(self.ae_pkg_path, 'w')

    def __del__(self):
        type(self).counter -= 1
        #os.remove(self.ae_file.name)


    # TODO
    #def add_apps(self,apps):
    #    for app in apps:
    #        pass

    # Wrapper for self.parse
    def load_ae_model(self,source):
        self.parse(source)

    # TODO
    #def remove_app_ensemble(self):
    #    os.remove(self.ae_file.name)
    #    del(self)

    def has_bpm(self):
        return self.has_file(self.bpmn_filename)

    def get_bpm(self):
        return self.get_file(self.bpmn_filename)

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
                raise IOError('File "%s" not found in AppEnsemble' % filename)

    def getRequiredApps(self,use_json=False):
        #TODO: Adapt to new ontology

        res = self.query("""
            PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
            PREFIX bpmn2: <http://dkm.fbk.eu/index.php/BPMN2_Ontology#>
            SELECT DISTINCT ?app_uri ?name ?original_name
            WHERE {
                [] aof:assignedApp ?app_uri;
                   bpmn2:Name ?name .

                ?app_uri rdfs:label ?original_name .
            }
        """)
        if use_json:
            result=list()
            for row in res.bindings:
                tmp=dict()
                for col in row:
                    tmp[str(col)]=str(row[col])
                result.append(tmp)
            res=result
        return res

    def getDocumentation(self):
        try:
            a = self.identifier
            doc = self.value(subject=self.getURI(), predicate=BPMN2.documentation, any=False)
            return doc
        except:
            return " "

    def getURI(self):
        try:
            uri = self.value(predicate=RDF.type, object=AOF.isAppEnsemble, any=False)
            return uri
        except:
            return " "

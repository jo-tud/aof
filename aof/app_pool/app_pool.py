from rdflib import Graph, ConjunctiveGraph, URIRef, Namespace, RDF, RDFS, BNode, Literal
from rdflib.plugins.memory import IOMemory
from rdflib.plugins.sparql.algebra import triples
from pyramid.path import AssetResolver

import os # os abstraction (e.g. listdir)

import sys # e.g. for exit()

class LocalAppPool:
    def __init__(self):
        def createStore(self):
            # Load the App Pool descriptions
            store = IOMemory()
            self.ap = Graph(store=store,identifier="ap")

        def loadFromFilesystem(self):
            for file in os.listdir(self.DATA_FOLDER):
                if file.endswith(".ttl"):
                    # print(file)
                    self.ap.parse(os.path.join(self.DATA_FOLDER,file), format = "turtle")
                 
        createStore(self)
        loadFromFilesystem(self)
    
    ''' Returns the result of a query as JSON
    '''
    def queryAP(self, qstr):
        # print("Query: ",qstr)
        res = self.ap.query(qstr)
        # print("Result: \n\n",res.serialize(format = 'txt').decode())
        return res.serialize(format = 'json')
        return 'hahaha'

    def printAppList(self):
        query = """
        PREFIX ap: <http://eatld.et.tu-dresden.de/ap/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT * 
        WHERE { 
            ?app_uri a ap:App .
            ?app_uri rdfs:label ?label .
        } 
        LIMIT 10
        """
        res = self.ap.query(query)
        print(res.serialize(format = 'txt').decode())
        
    ''' turns a relative path (below the aof directory) into an absolute path
    '''
    def getAbsPath(relative_path):
      a = AssetResolver('aof')
      resolver = a.resolve(relative_path)
      return resolver.abspath()
    
    ''' Static code
    '''
    DATA_FOLDER = getAbsPath('app_pool/data/')


# Will only be called when executed from shell
if __name__ == "__main__":
    lap = LocalAppPool()
    lap.printAppList()
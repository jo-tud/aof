from rdflib import Graph, ConjunctiveGraph, URIRef, Namespace, RDF, RDFS, BNode, Literal
from pyramid.path import AssetResolver
from aof.tools.AOFGraph import AOFGraph, AOF
from aof.tools.Singleton import Singleton

import os # os abstraction (e.g. listdir)
import logging


@Singleton
class AppPool(Graph):
    def __init__(self, init_data_URI=None):
        g = AOFGraph.Instance()
        Graph.__init__(self, store=g.store, identifier=AOF.AppPool)

        self.log = logging.getLogger(__name__)

        self.init_data_URI = init_data_URI
        if self.init_data_URI:
            try:
                self.parse(self.init_data_URI)
            except:
                self.log.error("There was a problem connecting to %s." %self.init_data_URI)


        def loadAppDescriptions(self):
            for s, p, o in self.triples( (None, AOF.hasAppDescription, None) ):
                try:
                    self.parse(o)
                except:
                    self.log.error("There was a problem connecting to %s." %o)

        loadAppDescriptions(self)
    
    ''' Returns the result of a query as JSON
    '''
    def queryAP(self, qstr):
        # print("Query: ",qstr)
        res = self.ap.query(qstr)
        # print("Result: \n\n",res.serialize(format = 'txt').decode())
        return res.serialize(format = 'json')

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
        res = self.query(query)
        print(res.serialize(format = 'txt').decode())
        
    ''' turns a relative path (below the aof directory) into an absolute path
    '''
    def getAbsPath(relative_path):
      a = AssetResolver('aof')
      resolver = a.resolve(relative_path)
      return resolver.abspath()
    
    ''' Static code
    '''
    DATA_FOLDER = getAbsPath('static/data/')


# Will only be called when executed from shell
if __name__ == "__main__":
    ap = AppPool.Instance("http://localhost:8081/static/App-Pool/pool.ttl")
    print("This graph is a singleton and currently contains %i triples" %(ap.__len__() ) )
    print("\nThe Graph:\n\n",ap.serialize(format="turtle", indent=1).decode())

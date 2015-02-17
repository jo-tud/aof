from rdflib import Graph, util
from pyramid.path import AssetResolver
from aof.tools.AOFGraph import AOFGraph, AOF
from aof.tools.Singleton import Singleton

import logging

@Singleton
class AppPool(Graph):
    init_source = None
    def __init__(self, source=None, format=None):
        """
            :Parameters:

        - `source`: An InputSource, file-like object, or string. In the case
        of a string the string is the location of the source.
        - `format`: Used if format can not be determined from source.
        Defaults to rdf/xml. Format support can be extended with plugins,
        but 'xml', 'n3', 'nt', 'trix', 'rdfa' are built in.
        """
        g = AOFGraph.Instance()
        Graph.__init__(self, store=g.store, identifier=AOF.AppPool)

        self.log = logging.getLogger(__name__)
        if source:
            if self.init_source:
                self.log.error("App-Pool was already initialized from %s. Ignoring %s." % self.init_source, source)
            else:
                self.init_source = source
                try:
                    self.parse(source=source, format=format)
                    self.log.info("Initialized App-Pool from %s. This should happen only once." % self.init_source)
                except AssertionError:
                    self.log.error(Exception)
                    self.log.error("There was a problem with initializing the App-Pool from %s" % self.init_source)
        else:
            self.log.debug("Initialized App-Pool. This should happen only once!")

        def loadAppDescriptions(self):
            for s, p, o in self.triples( (None, AOF.hasAppDescription, None) ):
                try:
                    self.parse(source=o, format=util.guess_format(o))
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

    ap = AppPool.Instance("http://domain.de/foo.ttl")
    print("This graph is a singleton and currently contains %i triples" %(ap.__len__() ) )
    print("\nThe Graph:\n\n",ap.serialize(format="turtle", indent=1).decode())

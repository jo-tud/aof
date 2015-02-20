from rdflib import ConjunctiveGraph, util
from pyramid.path import AssetResolver
from aof.tools.AOFGraph import AOFGraph
from aof.tools.namespaces import AOF
from aof.tools.Singleton import Singleton

import logging

__all__ = [
    'AppPool'
]

@Singleton
class AppPool(ConjunctiveGraph):
    init_source = None
    def __init__(self, source=None, format=None):
        """
        @param string source: An InputSource, file-like object, or string. In the case of a string the string is the location of the source.
        @param string format: Must be given if format can not be determined from source, 'xml', 'n3', 'nt', 'trix', and 'rdfa' are built in.
        """
        g = AOFGraph.Instance()
        ConjunctiveGraph.__init__(self, store=g.store, identifier=AOF.AppPool)

        self.log = logging.getLogger(__name__)
        if source:
            if self.init_source:
                self.log.error("App-Pool was already initialized from %s. Ignoring %s." % self.init_source, source)
            else:
                self.init_source = source
                try:
                    self.parse(source=source, format=format)
                    self.log.info("Initialized App-Pool from %s. This should happen only once." % self.init_source)
                except:
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
    def update_app_pool(self, source=None, format=None):
        self.init_source = None
        self._clear_app_pool()
        AppPool.Instance().__init__(source, format)

    ''' Clear the App-Pool
    '''
    def _clear_app_pool(self):
        self.remove((None, None, None))


# Will only be called when executed from shell
if __name__ == "__main__":
    ap = AppPool.Instance("http://localhost:8081/static/App-Pool/pool.ttl")

    ap = AppPool.Instance("http://domain.de/foo.ttl")
    print("This graph is a singleton and currently contains %i triples" %(ap.__len__() ) )
    print("\nThe Graph:\n\n",ap.serialize(format="turtle", indent=1).decode())

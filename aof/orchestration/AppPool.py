from rdflib import ConjunctiveGraph, util, URIRef
from pyramid.path import AssetResolver
from aof.orchestration.AOFGraph import AOFGraph
from aof.orchestration.namespaces import AOF
from aof.orchestration.Singleton import Singleton
from rdflib.namespace import DC, FOAF, RDF, RDFS

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
                    self.log.error("There was a problem reading %s." %o)

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

    def getNumberOfApps(self):
        query = """
       PREFIX aof: <%(AOF)s>
        SELECT DISTINCT ?app
        WHERE {
        # ?app a aof:App .
        ?app aof:currentBinary ?binary
        }
        """ % {'AOF': str(AOF)}
        test = self.query(query)
        return len(self.query(query).bindings)

    def getAppURIs(self):
        """
        List of URI identifiers as URIRefs for all apps in the pool
        """
        app_uris = list()
        # TODO: Implement better method to find all apps
        # e.g.: for app_uri in self.objects(RDF.type, AOF.AndroidApp):

        for app_uri in self.subjects(AOF.currentBinary):
            app_uris.append(app_uri)
        return app_uris

    def getAppName(self, identifier):
        """
        Returns the of an app identified by a given identifier.
        """
        subject = URIRef (identifier)
        predicate = RDFS.label
        app_name = self.value(subject, predicate)
        return app_name

    def getAppIconURI(self, identifier):
        """
        Returns the icon URI for a an app identified by a given identifier.
        """
        subject = URIRef (identifier)
        predicate = AOF.hasIcon
        icon_uri = self.value(subject, predicate)
        return icon_uri

    def getAppCurrentBinaryURI(self, identifier):
        """
        Returns the binary URI for a an app identified by a given identifier.
        """
        subject = URIRef (identifier)
        predicate = AOF.currentBinary
        icon_uri = self.value(subject, predicate)
        return icon_uri

    def isAndroidApp(self, identifier):
        """
        Returns True if app is an Android app otherwise returns False
        """
        q = ("""
            ASK WHERE {
                    <%(uri)s> a aof:AndroidApp .
            }
        """) % {'uri': identifier}
        return self.query(q).askAnswer


# Will only be called when executed from shell
if __name__ == "__main__":
    import os
    os.chdir("/home/jo/Dokumente/Orchestration/AOF")
    ap = AppPool.Instance("http://localhost:8081/static/App-Pool/pool.ttl")

    print("This graph is a singleton and currently contains %i triples" %(ap.__len__() ) )
    print(ap.getNumberOfApps())
    print("App URIs: " + str(ap.getAppURIs()))
    print("An icon URI: " + str(ap.getAppIconURI("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AppEnsembleInstaller")))

    print("An app name: " + str(ap.getAppName("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AppEnsembleInstaller")))
    print("Is this and Android app? " + str(ap.isAndroidApp("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AppEnsembleInstaller")))
    #print("\nThe Graph:\n\n",ap.serialize(format="turtle", indent=1).decode())

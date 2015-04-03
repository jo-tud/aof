from rdflib import ConjunctiveGraph, util, URIRef
from aof.orchestration.Singleton import Singleton
from aof.orchestration.AOFGraph import AOFGraph
from aof.orchestration.namespaces import AOF, ANDROID
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

    def get_number_of_apps(self):
        q = """
        SELECT DISTINCT ?app
        WHERE {
        # ?app a aof:App .
        ?app aof:currentBinary ?binary
        }
        """
        return len(self.query(q).bindings)

    def get_app_uris(self):
        """
        List of URI resources as URIRefs for all apps in the pool
        """
        app_uris = list()
        # TODO: Implement better method to find all apps
        # e.g.: for app_uri in self.objects(RDF.type, AOF.AndroidApp):

        for app_uri in self.subjects(AOF.currentBinary):
            app_uris.append(app_uri)
        return app_uris

    def get_name(self, resource):
        """
        Returns the of an app identified by a given resource.
        """
        app_name = self.value(resource, RDFS.label)
        return app_name

    def get_description(self, resource):
        """
        Returns the of an app identified by a given resource.
        """
        return self.value(resource, RDFS.comment)

    def get_icon_uri(self, resource):
        """
        Returns the icon URI for a an app identified by a given resource.
        """
        return self.value(resource, AOF.hasIcon)

    def get_binary_uri(self, resource):
        """
        Returns the binary URI for a an app identified by a given resource.
        """
        return self.value(resource, AOF.currentBinary)

    def has_role(self,resource):
        """
        Returns True if app has a specified role, otherwise returns False.
        """
        q = ("ASK WHERE {<%(uri)s> aof:hasRole ?role .}") % {'uri': resource}
        return self.query(q).askAnswer

    def get_roles(self, resource):
        """
        Returns a list of roles the app has
        """
        roles_iter = self.objects(resource, AOF.hasRole)
        roles = list()
        for role in roles_iter:
            roles.append(role)
        return roles

    def is_android_app(self, resource):
        """
        Returns True if app is an Android app, otherwise returns False.
        """
        q = ("ASK WHERE {<%(uri)s> a aof:AndroidApp .}") % {'uri': resource}
        return self.query(q).askAnswer

    def has_main_screenshot(self, resource):
        """
        Returns True if app has at least one screenshot, otherwise returns False
        """
        return ((resource, AOF.MainScreenshot, None) in self)

    def get_main_screenshot(self, resource):
        """
        Returns a dictionary of the main screenshot URI thumbnail URI and comment
        """
        main_screenshot = self.value(resource, AOF.MainScreenshot)
        return {
            'uri': self.value(main_screenshot, AOF.hasScreenshot),
            'thumb_uri': self.value(main_screenshot, AOF.hasScreenshotThumbnail),
            'comment': self.value(main_screenshot, RDFS.comment)
        }

    def has_other_screenshots(self, resource):
        """
        Returns True if app has at least one screenshot, otherwise returns False
        """
        if ((resource, AOF.Screenshot, None) in self):
            return True
        else:
            return False

    def get_other_screenshots(self, resource):
        """
        Returns a list of dictionaries of screenshot URI thumbnail URI and comment.
        """
        screenshots = list()
        for screenshot in self.objects(resource, AOF.Screenshot):
            screenshots.append(
                {
                    'uri': self.value(screenshot, AOF.hasScreenshot),
                    'thumb_uri': self.value(screenshot, AOF.hasScreenshotThumbnail),
                    'comment': self.value(screenshot, RDFS.comment)
                }
            )
        return screenshots

    def has_creator(self, resource):
        """
        Returns True if app has at least one creator, otherwise returns False.
        """
        return ((resource, DC.creator, None) in self)

    def get_creators(self, resource):
        """
        Returns a list of dictionaries of creator uri, name, mbox and homepage..
        """
        creators = list()
        for creator in self.objects(resource, DC.creator):
            creators.append(
                {
                    'uri': creator,
                    'name': self.value(creator, FOAF.name),
                    'mbox': self.value(creator, FOAF.mbox),
                    'homepage': self.value(creator, FOAF.homepage)
                }
            )
        return creators

    def has_entry_points(self, resource):
        """
        Returns True if app has at least one entry point, otherwise returns False.
        """
        return ((resource, AOF.providesEntryPoint, None) in self)

    def get_entry_points(self, resource):
        """
        Returns a list of dictionaries of creator uri, name, mbox and homepage..
        """
        entry_points = list()
        for ep in self.objects(resource, AOF.providesEntryPoint):
            ep_details = {
                'uri': ep,
                'types': self.objects(ep, RDF.type),
                'android_name': self.value(ep, ANDROID.name),
                'label': self.value(ep, RDFS.label),
                'comment': self.value(ep, RDFS.comment)
                }
            if self.has_inputs(ep):
               ep_details['inputs'] = self.get_inputs(ep)
            entry_points.append(ep_details)
        return entry_points

    def has_inputs(self, entry_point):
        """
        Returns True if app has at least one input, otherwise returns False.
        """
        return ((entry_point, AOF.hasInput, None) in self)

    def get_inputs(self, entry_point):
        """
        Returns a list of inputs for a given entry point.
        :return: List of inputs as dictionaries
        """
        inputs = list()
        for input in self.objects(entry_point, AOF.hasInput):
            inputs.append({
                'uri': input,
                'types': self.objects(input, RDF.type),
                'android_name': self.value(input, ANDROID.name),
                'is_required': self.value(input, AOF.isRequired),
                'data_type': self.value(input, AOF.datatype),
                'comment': self.value(input, RDFS.comment)
                })
        return inputs

    def has_exit_points(self, resource):
        """
        Returns True if app has at least one exit point, otherwise returns False.
        """
        return (resource, AOF.providesExitPoint, None) in self

    def get_exit_points(self, resource):
        """
        Returns a list of dictionaries of creator uri, name, mbox and homepage..
        """
        exit_points = list()
        for ep in self.objects(resource, AOF.providesExitPoint):
            ep_details ={
                    'uri': ep,
                    'types': self.objects(ep, RDF.type),
                    'label': self.value(ep, RDFS.label),
                    'comment': self.value(ep, RDFS.comment)
                }
            if self.has_outputs(ep):
               ep_details['outputs'] = self.get_outputs(ep)
            exit_points.append(ep_details)
        return exit_points

    def has_outputs(self, exit_point):
        """
        Returns True if app has at least one output, otherwise returns False.
        """
        return ((exit_point, AOF.hasOutput, None) in self)

    def get_outputs(self, exit_point):
        """
        Returns a list of inputs for a given exit point.
        :return: List of outputs as dictionaries
        """
        inputs = list()
        for output in self.objects(exit_point, AOF.hasOutput):
            inputs.append(
                {
                    'uri': output,
                    'types': self.objects(output, RDF.type),
                    'android_name': self.value(output, ANDROID.name),
                    'is_guaranteed': self.value(output, AOF.isGuaranteed),
                    'data_type': self.value(output, AOF.datatype),
                    'comment': self.value(output, RDFS.comment)
                }
            )
        return inputs


# Will only be called when executed from shell
if __name__ == "__main__":
    import os
    os.chdir("/home/jo/Dokumente/Orchestration/AOF")
    ap = AppPool.Instance("http://localhost:8081/static/App-Pool/pool.ttl")

    print("This graph is a singleton and currently contains %i triples" %(ap.__len__() ) )
    print(ap.get_number_of_apps())
    print("App URIs: " + str(ap.get_app_uris()))
    print("An icon URI: " + str(ap.get_icon_uri(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))

    print("An app name: " + str(ap.get_name(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
    print("An app description: " + str(ap.get_description(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
    print("Is this and Android app? " + str(ap.is_android_app(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
    print("Does this app have a role? " + str(ap.has_role(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
    print("Some app roles: " + str(ap.get_roles(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))

    print("Does this app have a screenshot? " + str(ap.has_main_screenshot(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
    print("A main screenshot: " + str(ap.get_main_screenshot(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))

    print("Does this app have other screenshots? " + str(ap.has_other_screenshots(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
    print("Some other screenshots: " + str(ap.get_other_screenshots(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))

    print("Does this app have a creator? " + str(ap.has_creator(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
    print("The creators: " + str(ap.get_creators(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))

    print("Does this app have entry points? " + str(ap.has_entry_points(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
    if ap.has_entry_points(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor")):
        print("These are the entry points: " + str(ap.get_entry_points(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
        an_entry_point = ap.get_entry_points(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))[0]['uri']
        print("Does this entry point have inputs? " + str(ap.has_inputs(an_entry_point)))
        if ap.has_inputs(an_entry_point):
            print("Some inputs: " + str(ap.get_inputs(an_entry_point)))

    print("Does this app have exit points? " + str(ap.has_exit_points(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
    if ap.has_exit_points(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor")):
        print("These are the exit points: " + str(ap.get_exit_points(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))))
        an_exit_point = ap.get_exit_points(URIRef("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor"))[0]['uri']
        print("Does this exit point have inputs? " + str(ap.has_outputs(an_exit_point)))
        if ap.has_outputs(an_exit_point):
            print("Some outputs: " + str(ap.get_outputs(an_exit_point)))

    #print("\nThe Graph:\n\n",ap.serialize(format="turtle", indent=1).decode())

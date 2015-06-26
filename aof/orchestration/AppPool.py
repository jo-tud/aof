from rdflib import ConjunctiveGraph, util, URIRef
from aof.orchestration.Singleton import Singleton
from aof.orchestration.AOFGraph import AOFGraph
from pyramid.path import AssetResolver
import os.path
from aof.orchestration.namespaces import AOF, ANDROID
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, RDFS
from pyramid.threadlocal import get_current_registry

import requests
import requests.exceptions

import logging
import inspect

__all__ = [
    'AppPool'
]

@Singleton
class AppPool(ConjunctiveGraph):
    init_source = "aof:resources/App-Pool/pool.ttl"
    init_format="turtle"

    def __init__(self):
        g = AOFGraph.Instance()
        ConjunctiveGraph.__init__(self, store=g.store, identifier=AOF.AppPool)

        self.log = logging.getLogger(__name__)

        registry = get_current_registry()
        if (registry.settings is not None) and ('app_pool_path' in registry.settings):
            self.init_source=registry.settings['app_pool_path']



        self.add_apps_from_app_pool_definition(source=self.init_source, format=self.init_format)

    def add_apps_from_app_pool_definition(self, source=None, format=None):
        """
        Adds apps to the pool from a given app-pool definition source which contains statements in the form:
        [] aof:hasAppDescription "[URI to app-description]" .

        @param string source: An InputSource, file-like object, or string. In the case of a string the string is the location of the source.
        @param string format: Must be given if format can not be determined from source, 'xml', 'n3', 'nt', 'trix', 'turtle' and 'rdfa' are built in.
        """
        self.clear_app_pool()

        if source==None:
            source=self.init_source
            if format==None:
                format=self.init_format
        try:

            a = AssetResolver()
            source = a.resolve(source).abspath()
            self.parse(source=source, format=format)
            self.log.info("Added apps from %s." % source)
        except:
            self.log.error("There was a problem with adding apps to the App-Pool from %s" % source)
            self.log.error(Exception)

        basedir=source.rpartition(os.sep)
        basedir=basedir[0]+basedir[1]

        a=AssetResolver()

        for s, p, o in self.triples( (None, AOF.hasAppDescription, None) ):
            try:
                # Checking whether the path is relative or not. If is then resolve it
                if not (o.startswith('http://') or o.startswith('/')):
                    o=a.resolve(os.path.abspath(basedir+o)).abspath()

                self.parse(source=o, format=util.guess_format(o))
            except SyntaxError as detail:
                self.log.error("There was a syntax error reading %s." %o)
                self.log.error(detail)
            except Exception as detail:
                self.log.error("There was a problem reading %s." %o)
                self.log.error(detail)



    def clear_app_pool(self):
        ''' Clear the App-Pool
        '''
        self.remove((None, None, None))
        self.log.info("Cleared the App-Pool.")

    def get_number_of_apps(self):
        q = """
        SELECT DISTINCT ?app
        WHERE {
        # ?app a aof:App .
        ?app aof:hasInstallableArtifact ?installable
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

        for app_uri in self.subjects(AOF.hasInstallableArtifact):
            app_uris.append(app_uri)
        return app_uris

    def get_name(self, resource):
        """
        Returns the of an app identified by a given resource.
        """
        app_name = self.value(resource, RDFS.label)
        return app_name.__str__()

    def get_description(self, resource):
        """
        Returns the of an app identified by a given resource.
        """
        return self.value(resource, RDFS.comment).__str__()

    def get_icon_uri(self, resource):
        """
        Returns the icon URI for a an app identified by a given resource.
        """
        return self.value(resource, AOF.hasIcon).__str__()

    def get_install_uri(self, resource):
        """
        Returns the binary URI for a an app identified by a given resource.
        """
        return self.value(resource, AOF.hasInstallableArtifact).__str__()

    def has_role(self,resource):
        """
        Returns True if app has a specified role, otherwise returns False.
        """
        q = ("ASK WHERE {<%(uri)s> aof:hasAppEnsembleRole ?role .}") % {'uri': resource}
        return self.query(q).askAnswer

    def get_roles(self, resource):
        """
        Returns a list of roles the app has
        """
        roles_iter = self.objects(resource, AOF.hasAppEnsembleRole)
        roles = list()
        for role in roles_iter:
            roles.append(role.__str__())
        return roles

    def in_pool(self, resource):
        """
        Searches for an specific AppEnsemble.
        :param resource: String (Name of the App
        :return:Boolean
        """
        q = ("ASK WHERE {<%(uri)s> ?p ?o .}")% {'uri': URIRef(resource)}
        return self.query(q).askAnswer


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
        return ((resource, AOF.hasMainScreenshot, None) in self)

    def get_main_screenshot(self, resource):
        """
        Returns a dictionary of the main screenshot URI thumbnail URI and comment
        """
        main_screenshot = self.value(resource, AOF.hasMainScreenshot)
        return {
            'uri': self.value(main_screenshot, FOAF.depiction).__str__(),
            'comment': self.value(main_screenshot, RDFS.comment).__str__()
        }

    def has_other_screenshots(self, resource):
        """
        Returns True if app has at least one screenshot, otherwise returns False
        """
        if (resource, AOF.hasScreenshot, None) in self:
            return True
        else:
            return False

    def get_other_screenshots(self, resource):
        """
        Returns a list of dictionaries of screenshot URI thumbnail URI and comment.
        """
        screenshots = list()
        for screenshot in self.objects(resource, AOF.hasScreenshot):
            screenshots.append(
                {
                    'uri': self.value(screenshot, FOAF.depiction).__str__(),
                    'comment': self.value(screenshot, RDFS.comment).__str__()
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
                    'uri': creator.__str__(),
                    'name': self.value(creator, FOAF.name).__str__(),
                    'mbox': self.value(creator, FOAF.mbox).__str__(),
                    'homepage': self.value(creator, FOAF.homepage).__str__()
                }
            )
        return creators

    def has_entry_points(self, resource):
        """
        Returns True if app has at least one entry point, otherwise returns False.
        """
        return ((resource, AOF.hasEntryPoint, None) in self)

    def get_entry_points(self, resource):
        """
        Returns a list of dictionaries of creator uri, name, mbox and homepage..
        """
        entry_points = list()
        for ep in self.objects(resource, AOF.hasEntryPoint):
            ep_details = {
                'uri': ep.__str__(),
                'types': self.objects(ep, RDF.type),
                'android_name': self.value(ep, ANDROID.name).__str__(),
                'label': self.value(ep, RDFS.label).__str__(),
                'comment': self.value(ep, RDFS.comment).__str__()
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
                'uri': input.__str__(),
                'types': self.objects(input, RDF.type),
                'android_name': self.value(input, ANDROID.name).__str__(),
                'is_required': self.value(input, AOF.isRequired),
                'has_datatype': self.value(input, AOF.hasDatatype).__str__(),
                'comment': self.value(input, RDFS.comment).__str__()
                })
        return inputs

    def has_exit_points(self, resource):
        """
        Returns True if app has at least one exit point, otherwise returns False.
        """
        return (resource, AOF.hasExitPoint, None) in self

    def get_exit_points(self, resource):
        """
        Returns a list of dictionaries of creator uri, name, mbox and homepage..
        """
        exit_points = list()
        for ep in self.objects(resource, AOF.hasExitPoint):
            ep_details ={
                    'uri': ep.__str__(),
                    'types': self.objects(ep, RDF.type),
                    'label': self.value(ep, RDFS.label).__str__(),
                    'comment': self.value(ep, RDFS.comment).__str__()
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
                    'uri': output.__str__(),
                    'types': self.objects(output, RDF.type),
                    'android_name': self.value(output, ANDROID.name).__str__(),
                    'is_guaranteed': self.value(output, AOF.isGuaranteed),
                    'has_datatype': self.value(output, AOF.hasDatatype).__str__(),
                    'comment': self.value(output, RDFS.comment).__str__()
                }
            )
        return inputs

    def get_build_number(self,resource):
        build_number_uri = self.value(resource, AOF.hasVersion)
        build_number_doc=build_number=self.value(resource,AOF.version)
        if build_number_uri != None:
            try:
                r = requests.get(build_number_uri,timeout=0.1) # timeout 100ms
                r.raise_for_status()
                build_number=r.text
            except:
                if build_number_doc != None:
                    build_number=build_number_doc
                else:
                    build_number=None
        elif build_number_doc != None:
            build_number=build_number_doc
        else:
            build_number=None

        return build_number
from rdflib import  util, URIRef
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


__all__ = [
    'AppPool'
]

@Singleton
class AppPool(AOFGraph):
    init_source = "aof:resources/App-Pool/pool.ttl"
    init_format="turtle"


    def __init__(self):
        AOFGraph.__init__(self,AOF.AppPool)

        self.log = logging.getLogger(__name__)

        registry = get_current_registry()
        if (registry.settings is not None) and ('app_pool_path' in registry.settings):
            self.init_source=registry.settings['app_pool_path']

        self.load(source=self.init_source, format=self.init_format)


    def load(self, source=None, format=None):
        """
        Adds apps to the pool from a given app-pool definition source which contains statements in the form:
        [] aof:hasAppDescription "[URI to app-description]" .

        @param string source: An InputSource, file-like object, or string. In the case of a string the string is the location of the source.
        @param string format: Must be given if format can not be determined from source, 'xml', 'n3', 'nt', 'trix', 'turtle' and 'rdfa' are built in.
        """
        self.clear()

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

                super().load(source=o, format=util.guess_format(o))
            except SyntaxError as detail:
                self.log.error("There was a syntax error reading %s." %o)
                self.log.error(detail)
            except Exception as detail:
                self.log.error("There was a problem reading %s." %o)
                self.log.error(detail)


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
        return self.get_tuple(resource, RDFS.label,to_string=True)


    def get_description(self, resource):
        """
        Returns the of an app identified by a given resource.
        """
        return self.get_tuple(resource, RDFS.comment,to_string=True)

    def get_icon_uri(self, resource):
        """
        Returns the icon URI for a an app identified by a given resource.
        """
        return self.get_tuple(resource, AOF.hasIcon,to_string=True)

    def get_install_uri(self, resource):
        """
        Returns the binary URI for a an app identified by a given resource.
        """
        return self.get_tuple(resource, AOF.hasInstallableArtifact,to_string=True)

    def has_role(self,resource):
        """
        Returns True if app has a specified role, otherwise returns False.
        """
        return self.has_tuple(resource,AOF.hasAppEnsembleRole ,use_sparql=False)

    def get_roles(self, resource):
        """
        Returns a list of roles the app has
        """
        return self.get_tuples(resource, AOF.hasAppEnsembleRole)

    def is_android_app(self, resource):
        """
        Returns True if app is an Android app, otherwise returns False.
        """
        return self.is_resource_of_type(resource,AOF.AndroidApp)

    def has_main_screenshot(self, resource):
        """
        Returns True if app has at least one screenshot, otherwise returns False
        """
        return self.has_tuple(resource, AOF.hasMainScreenshot)

    def get_main_screenshot(self, resource):
        """
        Returns a dictionary of the main screenshot URI thumbnail URI and comment
        """
        main_screenshot = self.get_tuple(resource, AOF.hasMainScreenshot)

        predicate_dict= {'image_uri': FOAF.depiction, 'comment': RDFS.comment}
        return self.get_tuple_list(main_screenshot, predicate_dict, to_string=True)

    def has_other_screenshots(self, resource):
        """
        Returns True if app has at least one screenshot, otherwise returns False
        """
        return self.has_tuple(resource, AOF.hasScreenshot)

    def get_other_screenshots(self, resource):
        """
        Returns a list of dictionaries of screenshot URI thumbnail URI and comment.
        """
        sub_predicate_dict= {'image_uri': FOAF.depiction, 'comment': RDFS.comment}

        return self.get_tuples_with_subtuples_list(resource,AOF.hasScreenshot,sub_predicate_dict,to_string=True)

    def has_creator(self, resource):
        """
        Returns True if app has at least one creator, otherwise returns False.
        """
        return self.has_tuple(resource, DC.creator)

    # TODO (None,None,None) nicht anzeigen
    def get_creators(self, resource):
        """
        Returns a list of dictionaries of creator uri, name, mbox and homepage..
        """
        sub_predicate_dict= {'name': FOAF.name, 'mbox': FOAF.mbox, 'homepage': FOAF.homepage}

        return self.get_tuples_with_subtuples_list(resource,DC.creator,sub_predicate_dict,to_string=True)


    def has_entry_points(self, resource):
        """
        Returns True if app has at least one entry point, otherwise returns False.
        """
        return self.has_tuple(resource, AOF.hasEntryPoint)


    def get_entry_points(self, resource):
        """
        Returns a list of dictionaries of creator uri, name, mbox and homepage..
        """
        return self._get_entry_exit_points(resource,AOF.hasEntryPoint,'inputs')

    def has_inputs(self, entry_point):
        """
        Returns True if app has at least one input, otherwise returns False.
        """
        return self.has_tuple(entry_point, AOF.hasInput)

    def get_inputs(self, entry_point):
        """
        Returns a list of inputs for a given entry point.
        :return: List of inputs as dictionaries
        """

        sub_predicate_dict= {'types': RDF.type, 'android_name': ANDROID.name, 'is_required': AOF.isRequired,'has_datatype': AOF.hasDatatype,'comment':RDFS.comment}

        return self.get_tuples_with_subtuples_list(entry_point,AOF.hasInput,sub_predicate_dict,to_string=True)

    def has_exit_points(self, resource):
        """
        Returns True if app has at least one exit point, otherwise returns False.
        """
        return self.has_tuple(resource, AOF.hasExitPoint)

    def get_exit_points(self, resource):
        """
        Returns a list of dictionaries of creator uri, name, mbox and homepage..
        """
        return self._get_entry_exit_points(resource,AOF.hasExitPoint,'outputs')

    def has_outputs(self, exit_point):
        """
        Returns True if app has at least one output, otherwise returns False.
        """

        return self.has_tuple(exit_point, AOF.hasOutput)

    def get_outputs(self, exit_point):
        """
        Returns a list of inputs for a given exit point.
        :return: List of outputs as dictionaries
        """
        sub_predicate_dict= {'types': RDF.type, 'android_name': ANDROID.name, 'is_guaranteed': AOF.isGuaranteed,'has_datatype': AOF.hasDatatype,'comment':RDFS.comment}

        return self.get_tuples_with_subtuples_list(exit_point,AOF.hasOutput,sub_predicate_dict,to_string=True)

    def _get_entry_exit_points(self,resource,predicate,dict_key):
        """
        functionality for get_entry_points and get_exit_points
        :param resource:
        :param predicate:
        :param dict_key: String: 'inputs' or 'outputs'
        :return:
        """
        sub_predicate_dict= {'types': RDF.type, 'android_name': ANDROID.name, 'label': RDFS.label, 'comment':RDFS.comment}
        sub_predicate_cardinality_greater_one=['types']

        points = list()
        for p in self.get_tuples(resource, predicate):
            p_details = self.get_tuple_list(p, sub_predicate_dict,sub_predicate_cardinality_greater_one, to_string=True)

            if dict_key=="inputs" and self.has_inputs(p):
               p_details[dict_key] = self.get_inputs(p)
            elif dict_key=="outputs" and self.has_outputs(p):
                p_details[dict_key] = self.get_outputs(p)

            points.append(p_details)

        return points

    #TODO
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
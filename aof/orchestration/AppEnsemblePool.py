__author__ = 'Korbinian Hörfurter'
from rdflib import  URIRef,Literal
from aof.orchestration.Singleton import Singleton
from aof.orchestration.AppEnsemble import AppEnsemble
from aof.orchestration.AOFGraph import AOFGraph
from pyramid.path import AssetResolver
from pyramid.threadlocal import get_current_registry
from aof.orchestration.AppEnsemble import _ae_folder_path
from aof.orchestration.namespaces import AOF


import os
import logging


@Singleton
class AppEnsemblePool(AOFGraph):
    """
    The AppEnsemblePool is a Singleton which
    - indexes a folder and searches for AppEnsemble-Files (__init__)
    - gives information about:
        - elements contained (__contains__,has_AppEnsemble,__str__)
        - number of elements contained (__len__,__str__)
        - the current AppEnsemble-Folder-Path (get_ae_folder_path)
    - returns a specific AppEnsemble-Object (get_AppEnsemble)
    - relaods the AppEnsemble-Pool with a new path (set_ae_folder_path)
    """
    #TODO
    def __init__(self):
        """
        Set up the AppEnsemblePool and load the AppEnsembles from the standard path
        :return:None
        """
        self.log = logging.getLogger(__name__)

        AOFGraph.__init__(self,AOF.AppEnsemblePool)

        self._ae_folder_path=_ae_folder_path
        self._ae_folder_path_backup=self._ae_folder_path

        registry = get_current_registry()
        if registry is None:
            self._ae_folder_path=registry.settings['app_ensemble_folder']

        self.pool=dict()
        self.a = AssetResolver()
        self._load_AppEnsembles()

        self.itemtype=URIRef("http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#AppEnsemble")



    def __contains__(self, identifier):
        """
        Searches for an specific AppEnsemble.
        :param identifier: String (Name of the AppEnsemble i.e. testAppEnsemble.ae-> item=testAppEnsemble
        :return:Boolean
        """
        q ="""
            ASK
            WHERE
            {{?s  a <{0}>.?s  <{1}> "{2}".}}
            """.format(self.itemtype,URIRef("http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#Name"),Literal(identifier))

        return self.query(q).askAnswer

    def __len__(self):
        """
        Counts the number of AppEnsembles.
        :return:Integer
        """
        q = """
        SELECT DISTINCT ?app
        WHERE {{?app a <{0}> .}}
        """.format(self.itemtype)
        return len(self.query(q).bindings)

    #TODO
    def __str__(self):
        """
        Returns string with information about the Location and Number of AppEnsembles.
        :return:String
        """
        ae_list=", ".join(self.pool)
        return '___AppPoolManager-Details:___\nAppEnsemble-Location: {}\nAppEnsemble-List ({}): {}'.format(self.get_ae_folder_path(),self.__len__(),ae_list)

    #TODO
    def _load_AppEnsembles(self):
        """
        Indexes the AppEnsemble-Directory for files with the AppEnsemble-Extension and ADDs them to the AppEnsemblePool.
        :return:None
        """
        try:
            files = os.listdir(self.get_ae_folder_path())
            for file in files:
                if file.endswith(AppEnsemble.ae_extension):
                    identifier=file.replace(AppEnsemble.ae_extension,'')
                    ae_tmp=AppEnsemble(identifier)
                    self.pool[identifier]=ae_tmp
            ###########################################################  Hier weitermache... prüfen ob das wirklich eingelesen wird... etc.
            self.parse(source=os.path.join(self.get_ae_folder_path(),'testAppEnsemble','ae.ttl'), format="turtle")
            return None
        except FileNotFoundError as detail:
            if self._ae_folder_path != self._ae_folder_path_backup:
                self.log.error('AppEnsemble-Path "{}" was not found in the system! Try to use the standard path!'.format(self.get_ae_folder_path()))
                self.set_ae_folder_path(self._ae_folder_path_backup)
            else:
                self.log.error('AppEnsemble-Path "{}" was not found in the system!'.format(self.get_ae_folder_path()))
            return None
    #TODO
    def get_ae_folder_path(self):
        """
        Returns the absolute AppEnsemble-Folder-path
        :return:String
        """
        return self.a.resolve(self._ae_folder_path).abspath()
    #TODO
    def set_ae_folder_path(self,path):
        """
        Sets the new AppEnsemble-Folderpath and reloads the Apps into the AppEnsemblePool.
        :param path: String (i.e: "aof:static/test1/")
        :return: None
        """
        self._ae_folder_path=path
        self._load_AppEnsembles()
        return None
    #TODO
    def reload(self):
        """
        CLEARs the AppEnsemble-Pool and reloads the AppEnsembles into the pool.
        :return:None
        """
        self.pool.clear()
        self._load_AppEnsembles()
        return None

    def has_AppEnsemble(self,identifier):
        """
        Searches for the existence of a specific AppEnsemble.
        :param identifier: String (Name of the AppEnsemble i.e. testAppEnsemble.ae-> item=testAppEnsemble
        :return:Boolean
        """
        return self.__contains__(identifier)
    #TODO
    def get_AppEnsemble(self,identifier):
        """
        Searches for a specific AppEnsemble
        :param identifier: String (Name of the AppEnsemble i.e. testAppEnsemble.ae-> item=testAppEnsemble
        :return: AppEnsemble or None (if it does not exist)
        """
        identifier=str(identifier)
        try:
            return self.pool[identifier]
        except KeyError as detail:
            self.log.info('AppEnsemble "{}" was not found in the AppEnsemblePool!'.format(detail))
            return None

    def get_all_AppEnsembles(self):
        """
        Returns the whole AppEnsemble-Pool
        :return: dictionary
        """
        return self.pool
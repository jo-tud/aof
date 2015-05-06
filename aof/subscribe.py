__author__ = 'jo'
'''
This file should contain any event listeners for pyramid
'''

from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
from aof.orchestration.AppPool import AppPool
from aof.orchestration.AppEnsembleManager import AppEnsembleManager
from pyramid.path import AssetResolver
from pyramid.threadlocal import get_current_registry
"""
@subscriber(ApplicationCreated)
def after_application_created(event):
    # Initialize App-Pool
    registry = get_current_registry()
    settings = registry.settings

    a = AssetResolver()
    path = a.resolve(settings['app_pool_path']).abspath()

    ap = AppPool.Instance()
    ap.add_apps_from_app_pool_definition(source=path, format="turtle")

    aem=AppEnsembleManager.Instance()
    aem.set_ae_folder_path(settings['app_ensemble_folder'])"""

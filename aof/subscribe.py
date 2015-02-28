__author__ = 'jo'
'''
This file should contain any event listeners for pyramid
'''

from pyramid.events import ApplicationCreated
from pyramid.events import subscriber
from aof.orchestration.AppPool import AppPool
from pyramid.path import AssetResolver

@subscriber(ApplicationCreated)
def after_application_created(event):
    # Initialize App-Pool
    a = AssetResolver()
    path = a.resolve('aof:static/App-Pool/pool.ttl').abspath()

    AppPool.Instance(source=path,format="turtle")
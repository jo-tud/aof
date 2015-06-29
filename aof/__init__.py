from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import os
import aof.tmp

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """


    here = os.path.dirname(os.path.abspath(__file__))

    # session factory
    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

    config = Configurator(settings=settings, session_factory=session_factory)
    config.include('pyramid_chameleon')
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('tmp', 'tmp', cache_max_age=3600)
    
    # Routes
    config.add_route('home', '/')

    # App-Ensembles
    config.add_route('app-ensembles', '/app-ensembles.html')
    config.add_route('ae-details', '/app-ensembles/{URI}/details.html')
    config.add_route('ae-visualize-bpm', '/app-ensembles/{URI}/bpm.html')

    # App-Pool
    config.add_route('apps', '/apps.html')
    config.add_route('app-details','/apps/{URI:.*}/details.html')

    # Documentation
    config.add_route('documentation', '/docs/index.html')
    config.add_route('documentation-docs', '/docs/{document:.*}')
    config.add_route('documentation-resource', '/resources/{document}')

    # API

    ## Actions
    config.add_route('api-action-apps-update', '/api/actions/app-pool/update')
    config.add_route('api-action-appensembles-update', '/api/actions/app-ensembles/update')

    # API NEW
    config.add_route(pattern='/api/apps', name='api-apps') # TODO  certain format
    config.add_route(pattern='/api/apps/{URI:.*}/details', name='api-apps-app-details')
    config.add_route(pattern='/api/apps/{URI:.*}/version', name='api-apps-app-version')
    # TODO
    #config.add_route(pattern='/api/apps/{URI:.*}/apk', name='api-apps-app-apk')
    # Todo complexe Property wird mit node ausgegeben
    config.add_route(pattern='/api/apps/{URI:.*}/properties/{property:.*}', name='api-apps-app-property')
    # TODO: jquery put ermöglichen
    config.add_route(pattern='/api/app-ensembles', name='api-appensembles')
    #config.add_route(pattern='/api/app-ensembles/{URI:.*}/details', name='api-appensembles-ae')
    #config.add_route(pattern='/api/app-ensembles/{URI:.*}/bpmn', name='api-appensembles-ae-bpmn')
    config.add_route(pattern='/api/app-ensembles/{URI:.*}/package', name='api-appensembles-ae-package')
    config.add_route(pattern='/api/app-ensembles/{URI:.*}/bpmn', name='api-appensembles-ae-bpmn')



    config.scan()

    settings['mako.directories'] = os.path.join(here, 'templates')


    # Clear all temporary files
    aof.tmp.clear_all_tmp_files()
    # for a cronjob: function located in aof/tmp/__init__.py -> clear_all_tmp_files()

    return config.make_wsgi_app()

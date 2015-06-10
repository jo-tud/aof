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
    config.add_route('orchestrate', '/orchestrate.html')

    # App-Ensembles
    config.add_route('app-ensembles', '/app-ensembles.html')
    config.add_route('ae-details', '/app-ensembles/details.html')
    config.add_route('ae-visualize-bpm', '/app-ensembles/visualize-bpm.html')

    # App-Pool
    config.add_route('app-pool', '/app-pool.html')
    config.add_route('app-details','/app-pool/details.html')

    # Documentation
    config.add_route('documentation', '/docs/index.html')
    config.add_route('documentation-docs', '/docs/{document:.*}')
    config.add_route('documentation-resource', '/resources/{document}')

    # API
    ## JSON
    config.add_route('api-ae-json', '/api/app-ensembles.json')
    config.add_route('api-ap-json', '/api/app-pool.json')

    ## BPM
    config.add_route('ae-bpmn', '/app-ensembles/get-bpmn')

    ## Actions
    config.add_route('action-update-app-pool', '/api/actions/update-app-pool')
    config.add_route('action-update-ap-ensembles', '/api/actions/update-app-ensembles')

    ## Downloads
    config.add_route('api-get-ae-pkg', '/api/download/ae-package')

    ## TTL
    config.add_route('api-app-details','/api/app-pool/details.html')

    config.scan()

    settings['mako.directories'] = os.path.join(here, 'templates')


    # Clear all temporary files
    aof.tmp.clear_all_tmp_files()

    return config.make_wsgi_app()

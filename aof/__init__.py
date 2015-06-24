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
    config.add_route('ae-details-new','/app-ensembles/{URI}/details')
    config.add_route('ae-visualize-bpm', '/app-ensembles/visualize-bpm.html')

    # App-Pool
    config.add_route('app-pool', '/apps.html')
    config.add_route('app-details','/apps/details.html')
    #config.add_route('app-details-new','/apps/{URI:.*}/{a:.*}') # URI-Übergabe funktioniert nicht!!!


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
    config.add_route('api-app-details-show','/api/app-pool/details-show.html')

    # API NEW
    config.add_route(pattern='/api/apps', name='api-apps') # returns app-pool in certain format
    config.add_route(pattern='/api/apps/{URI:.*}/details', name='api-apps-app-details')
    config.add_route(pattern='/api/apps/{URI:.*}/version', name='api-apps-app-version')
    # TODO
    #config.add_route(pattern='/api/apps/{URI:.*}/apk', name='api-apps-app-apk')
    # Todo complexe Property wird mit node ausgegeben
    config.add_route(pattern='/api/apps/{URI:.*}/properties/{property:.*}', name='api-apps-app-property')

    config.add_route(pattern='/api/apps', request_method='put', name='api-apps-update') #update
    #config.add_route(pattern='/api/app-ensembles', name='api-appensembles')
    #config.add_route(pattern='/api/app-ensembles/{URI:.*}/details', name='api-appensembles-ae')
    #config.add_route(pattern='/api/app-ensembles/{URI:.*}/bpmn', name='api-appensembles-ae-bpmn')



    config.scan()

    settings['mako.directories'] = os.path.join(here, 'templates')




    # Clear all temporary files
    aof.tmp.clear_all_tmp_files()
    # for a cronjob: function located in aof/tmp/__init__.py -> clear_all_tmp_files()

    return config.make_wsgi_app()



"""
    config.add_route(pattern='/api/apps/*/details/*', name='') # *= pool, http%3A%2F%2Fdev.plt.et.tu-dresden.de%3A8085%2Fjenkins%2Fjob%2FAppEnsembleInstaller%2FlastSuccessfulBuild%2F

    config.add_route(pattern='/api/apps/apk', name='')
    config.add_route(pattern='/api/apps/version', name='')
    config.add_route(pattern='/api/apps/qrcode', name='')
    config.add_route(pattern='/api/app-pool/qrcode', name='')"""
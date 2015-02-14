from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import os

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    here = os.path.dirname(os.path.abspath(__file__))

    # session factory
    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

    config = Configurator(settings=settings)
    config = Configurator(settings=settings, session_factory=session_factory)
    config.include('pyramid_chameleon')
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    # Routes
    config.add_route('home', '/')
    config.add_route('orchestrate', '/orchestrate.html')

    config.add_route('deploy', '/deploy.html')
    config.add_route('app-pool', '/app-pool.html')

    config.add_route('demo', '/demo.html')
    config.add_route('demo_tool', '/demo/{tool}*')

    config.add_route('info', '/info.html')

    config.add_route('api', '/api/{tool}*')

    config.scan()

    settings['mako.directories'] = os.path.join(here, 'templates')

    return config.make_wsgi_app()

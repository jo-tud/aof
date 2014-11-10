from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    
    """ Route for app pool tools
    """
    config.add_route('ap_tools', '/ap/{tool}')
    
    """ Route for orchestration tools
    """
    config.add_route('o_tools', '/o/{tool}')
    
    config.add_route('dp_tools', '/dp/{tool}')
    
    config.add_route('dp_json', '/json/dp')

    config.scan()
    return config.make_wsgi_app()

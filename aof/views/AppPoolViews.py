from functools import wraps
from pyramid.response import Response
from pyramid.view import view_config
from aof.orchestration.AppPool import AppPool
from aof.orchestration.namespaces import AOF
from aof.views import namespaces
from aof.views.PageViews import PageViews, RequestPoolURI_Decorator
import logging

__author__ = 'khoerfurter'
log = logging.getLogger(__name__)

class AppCheckDecorator(object):
    """
    Decorator function:
    - Is the URI of the object the URI of an Android-App

    # Use this only for Methods only with an AppPool as class-attibute pool
    """

    def __call__(self, f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if (hasattr(self, "pool") and isinstance(self.pool, AppPool)):
                if self.pool.is_android_app(self.uri) != True:
                    return Response(
                        "The app '%s' doesn't seem to be an Android App. Currently only Android Apps are supported." % self.uri)
                else:
                    return f(self, *args, **kwargs)
            else:
                import inspect

                log.info('AppCheckDecorator is used for a method ({}) without AppPool!'.format(inspect.stack()[1][3]))
                return f(self, *args, **kwargs)

        return wrapper


class AppPoolViews(PageViews):
    def __init__(self, context, request):
        """
        Class with all AppPool-Pages and -Actions
        """
        super(AppPoolViews, self).__init__(context, request)
        self.pool = AppPool.Instance()

    @view_config(route_name='app-pool', renderer='aof:templates/app-pool.mako')
    def page_overview(self):
        """
        Generates the parameters for the AppPool-Homepage
        """
        self._setTitle('App-Pool')

        apps = list()
        app_uris = self.pool.get_app_uris()
        for app_uri in app_uris:
            app = {
                'uri': app_uri,
                'name': self.pool.get_name(app_uri),
                'icon': self.pool.get_icon_uri(app_uri),
                'binary': self.pool.get_install_uri(app_uri)
            }
            apps.append(app)

        apps = sorted(apps, key=lambda app: (app['name'], app['uri']))

        custom_args = {'apps': apps}
        return self._returnCustomDict(custom_args)

    @view_config(route_name='action-update-app-pool')
    def action_update(self):
        """
        Action: Update the AppPool from current AppPool definition
        :return: Response Object with number of Apps
        """
        self.pool.add_apps_from_app_pool_definition(source=None, format='turtle')
        res = str(self.pool.get_number_of_apps())
        return Response(res)

    @view_config(route_name='api-ap-json', renderer='json')
    def api_json(self):
        """
        Generates the pool in Json
        :return: json-representation of the AppPool
        """
        # log.debug("called view: ap_get_app_pool_json()")
        query = """
        PREFIX aof: <%(AOF)s>
        SELECT DISTINCT *
        WHERE {
        ?uri rdfs:label ?name ;
            aof:hasInstallableArtifact ?binary .
            OPTIONAL {
            ?uri aof:hasIcon ?icon
            }

        }
        ORDER BY ?name
        """ % {'AOF': str(AOF)}
        res = self.pool.query(query)
        json = res.serialize(format="json").decode()

        # log.debug(json)
        return {'json': json}

    @view_config(route_name='app-details', renderer='aof:templates/app-details.mako')
    @RequestPoolURI_Decorator()
    @AppCheckDecorator()
    def page_details(self):
        """
        Generates the Detail-Attributes for an given Request-URI
        :return: dictionary
        """
        self._setTitle('App-Details')
        details = {
            'name': self.pool.get_name(self.uri).__str__(),
            'comment': self.pool.get_description(self.uri).__str__(),
            'icon': self.pool.get_icon_uri(self.uri).__str__(),
            'binary': self.pool.get_install_uri(self.uri).__str__(),
            'has_role': self.pool.has_role(self.uri),
            'has_main_screenshot': self.pool.has_main_screenshot(self.uri),
            'has_other_screenshots': self.pool.has_other_screenshots(self.uri),
            'has_creator': self.pool.has_creator(self.uri),
            'has_entry_points': self.pool.has_entry_points(self.uri),
            'has_exit_points': self.pool.has_exit_points(self.uri)
        }
        if details['has_role']:
            roles = self.pool.get_roles(self.uri)
        else:
            roles = None

        if details['has_creator']:
            creators = self.pool.get_creators(self.uri)
        else:
            creators = None

        if details['has_main_screenshot']:
            main_screenshot = self.pool.get_main_screenshot(self.uri)
        else:
            main_screenshot = None

        if details['has_other_screenshots']:
            screenshots = self.pool.get_other_screenshots(self.uri)
        else:
            screenshots = None

        if details['has_entry_points']:
            entry_points = self.pool.get_entry_points(self.uri)
        else:
            entry_points = None

        if details['has_exit_points']:
            exit_points = self.pool.get_exit_points(self.uri)
        else:
            exit_points = None

        custom_args = {'namespaces': namespaces,
                       'uri': self.uri,
                       'qrcode': self._generateQRCode(details['binary']),
                       'details': details,
                       'roles': roles,
                       'creators': creators,
                       'main_screenshot': main_screenshot,
                       'screenshots': screenshots,
                       'entry_points': entry_points,
                       'exit_points': exit_points
                       }
        return self._returnCustomDict(custom_args)



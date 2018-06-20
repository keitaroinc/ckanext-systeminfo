import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
import ckanext.edsnews.helpers as _h
from ckanext.edsnews.model import setup as model_setup
from ckanext.edsnews.news_subscriptions_model import setup_news_subscriptions
from ckanext.edsnews.logic import auth

from routes.mapper import SubMapper

try:
    # CKAN 2.7 and later
    from ckan.common import config as _config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config as _config


class EdsnewsPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions, inherit=True)

    startup = False

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'edsnews')

        # IRouter

    def before_map(self, map):
        ctrl = 'ckanext.edsnews.controllers.edsnews:EdsnewsController'
        with SubMapper(map, controller=ctrl) as m:
            m.connect('news_index', '/news', action='news_index')

            m.connect('news_create', '/news/create',
                      action='news_create')
            m.connect('news_delete', '/news/delete/{id}',
                      action='news_delete')
            m.connect('news_show', '/news/{id}',
                      action='news_show')
            m.connect('news_update', '/news/update/{id}',
                      action='news_update')

        return map

    # IActions

    def get_actions(self):
        module_root = 'ckanext.edsnews.logic.action'
        action_functions = _h._scan_functions(module_root)
        return action_functions

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'news_create': auth.news_create,
            'news_update': auth.news_update,
            'news_patch': auth.news_patch,
            'news_delete': auth.news_delete,
            'news_subscription': auth.news_subscription,
            'news_mail_subscribed_users_show': auth.news_mail_subscribed_users_show
       }

    # IConfigurable

    def configure(self, config):
        self.startup = True

        # Setup news model
        model_setup()

        setup_news_subscriptions()

        self.startup = False

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'edsnews_get_current_url': _h.edsnews_get_current_url,
            'edsnews_get_recent_news': _h.edsnews_get_recent_news,
            'edsnews_truncate_limit': lambda : _config.get('ckanext.edsnews.truncate_limit', 100)
        }
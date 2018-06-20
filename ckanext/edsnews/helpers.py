# -*- coding: utf-8 -
import logging
import uuid
from urllib import urlencode

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

import ckan.model as m
import ckanext.edsnews.model as cm
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
from ckan.common import c, _, request

from ckanext.edsnews.news_subscriptions_model import ckanextNewsSubscriptions
import ckanext.eds.model.user_roles as _ur

log = logging.getLogger(__name__)


def _scan_functions(module_root, _functions={}):
    '''Helper function that scans extension for all logic/auth functions.'''
    for module_name in ['create', 'delete', 'get', 'patch', 'update']:
        module_path = '%s.%s' % (module_root, module_name,)

        module = __import__(module_path)

        for part in module_path.split('.')[1:]:
            module = getattr(module, part)

        for key, value in module.__dict__.items():
            if not key.startswith('_') and (hasattr(value, '__call__')
                                            and (value.__module__ == module_path)):
                _functions[key] = value
    return _functions


def user_is_sysadmin(context):
    '''
        Checks if the user defined in the context is a sysadmin
        rtype: boolean
    '''
    #TODO
    #It seems that this could be an unnecesarry call to the
    # user model. Querying the user model will potentially make calls to
    # the database, whereas the context object contains a 'auth_user_obj'
    # part of the 'user' context.
    model = context['model']
    user = context['user']
    user_obj = model.User.get(user)
    if not user_obj:
        log.error('User {0} not found').format(user)
        return False

    return user_obj.sysadmin


def user_is_editor(context):
    '''
        Checks if the user defined in the context is an editor 
        rtype: boolean
    '''
    roleObj =_ur.UserRoles.get(context['auth_user_obj'].id)
    if roleObj:
        if _ur.UserRoles.get(context['auth_user_obj'].id).role == "editor":
            return True
    return False


def user_is_registered(context):
    '''
        Checks if the user is registered user
    '''
    model = context['model']
    user = context['user']
    user_obj = model.User.get(user)
    if not user_obj:
        log.error('User {0} not found').format(user)
        return False

    return True


def edsnews_get_current_url(page, params, controller, action, exclude_param=''):
    url = h.url_for(controller=controller, action=action)
    for k, v in params:
        if k == exclude_param:
            params.remove((k, v))

    params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
              for k, v in params]

    url = url + u'?page=' + str(page)
    if (params):
        url = url + u'?page=' + str(page) + '&' + urlencode(params)

    return url


def edsnews_get_recent_news():
    limit = int(config.get('ckanext.edsnews.recent_news_limit', 5))
    _ = m.Session.query(cm.ckanextNews) \
        .order_by(cm.ckanextNews.created_at.desc()) \
        .limit(limit).all()
    return _


ctrl = 'ckanext.edsnews.controllers.edsnews:EdsnewsController'


def news_link(news_or_news_dict):
    if isinstance(news_or_news_dict, dict):
        name = news_or_news_dict['id']
    else:
        name = news_or_news_dict.id
    text = news_display_name(news_or_news_dict)
    return h.nav_link(
        text,
        controller=ctrl,
        action='news_show',
        id=name
    )


def news_display_name(news_or_news_dict):
    if isinstance(news_or_news_dict, dict):
        return news_or_news_dict.get('title', '') or \
               news_or_news_dict.get('name', '')
    else:
        return news_or_news_dict.title or news_or_news_dict.name


def user_subscribed_to_news(context, data_dict):
    model = context['model']
    user = context['user']
    user_obj = model.User.get(user)
    is_subscribed = ckanextNewsSubscriptions.get_subscription(user_obj.id)

    if is_subscribed:
        return True
    else:
        return False


def edsnews_get_users_mail(users_ids):
    import ckan.model as model

    mails = model.Session.query(model.User.email).filter(model.User.id.in_(users_ids)).all()
    out = [i[0] for i in mails]

    return out


def config_option_show(key, lang):
    _ = '{0}_{1}'.format(key, lang)
    res = ''
    try:
        res = toolkit.get_action('config_option_show')(dict(ignore_auth=True), {'key': _})
    except Exception as e:
        log.error(e)

    return res

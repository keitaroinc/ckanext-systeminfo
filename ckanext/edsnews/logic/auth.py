import logging

from ckan.plugins import toolkit as t
import ckanext.edsnews.helpers as _h

log = logging.getLogger(__name__)


def news_create(context, data_dict):
    '''
        Authorization check for news creation
    '''
    success = _h.user_is_sysadmin(context)
    if not success:
        success = _h.user_is_editor(context)
    out = {
        'success': success,
        'msg': '' if success else
        t._('User not authorized to create news')
    }
    return out


def news_update(context, data_dict):
    '''
        Authorization check for news update
    '''

    success = _h.user_is_sysadmin(context)
    if not success:
        success = _h.user_is_editor(context)
    out = {
        'success': success,
        'msg': '' if success else
        t._('User not authorized to update news')
    }
    return out


def news_patch(context, data_dict):
    '''
        Authorization check for news patch
    '''

    success = _h.user_is_sysadmin(context)
    if not success:
        success = _h.user_is_editor(context)
    out = {
        'success': success,
        'msg': '' if success else
        t._('User not authorized to patch news')
    }
    return out


def news_delete(context, data_dict):
    '''
        Authorization check for news delete
    '''
    success = _h.user_is_sysadmin(context)
    if not success:
        success = _h.user_is_editor(context)
    out = {
        'success': success,
        'msg': '' if success else
        t._('User not authorized to delete news')
    }
    return out

def news_subscription(context, data_dict):
    '''
        Authorization check for news subscriptions
    '''
    success = _h.user_is_registered(context)
    out = {
        'success': success,
        'msg': '' if success else
        t._('User not authorized to manage subscriptions')
    }
    return out

def news_mail_subscribed_users_show(context, data_dict):
    '''
        Authorization check for news delete
    '''
    success = _h.user_is_sysadmin(context)
    if not success:
        success = _h.user_is_editor(context)
    out = {
        'success': success
    }
    return out



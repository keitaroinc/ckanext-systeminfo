"""
ckanext-systeminfo
Copyright (c) 2018 Keitaro AB

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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



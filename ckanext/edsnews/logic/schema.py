"""
ckanext-systeminfo
Copyright (C) 2018  Keitaro AB

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
from datetime import datetime

from ckan.plugins import toolkit

from ckan.lib.navl.validators import (ignore_missing,
                                      not_empty,
                                      not_missing,
                                      ignore_empty
                                      )

#required to extend default activity_create validators
import ckanext.edsnews.logic.validators


log = logging.getLogger(__name__)


def news_create_schema():
    return {
        'title': [not_empty, unicode],
        'content': [ignore_missing, unicode],
        'meta': [ignore_missing, unicode],
        'expiration_date': [not_empty, expiration_not_in_past],
        'image_url': [ignore_missing, unicode]
    }


def news_update_schema():
    schema = news_create_schema()
    schema['id'] = [not_empty, unicode]
    return schema


def news_patch_schema():
    return news_update_schema()


def expiration_not_in_past(key, data, errors, context):
    expiration = data.get(key)

    if isinstance(expiration, basestring):
        try:
            expiration = datetime.strptime(expiration, '%Y-%m-%d')
            if expiration.date() < datetime.utcnow().date():
                errors[key].append(toolkit._('Expiration date is in the past'))
        except ValueError:
            errors[key].append(toolkit._('Incorrect expiration date format, should be YYYY-MM-DD'))
    else:
        if expiration.date() < datetime.utcnow().date():
            errors[key].append(toolkit._('Expiration date can not be in past'))


def news_subscription_schema():
    return {
        'notify_by_mail': [not_missing, custom_boolean_validator]
    }

def custom_boolean_validator(key, data, errors, context):
    value = data.get(key)
    if not isinstance(value, bool):
        errors[key].append(toolkit._('Incorrect type, should be boolean'))
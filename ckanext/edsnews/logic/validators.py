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

import ckan.lib.navl.dictization_functions as df

from ckan.common import _
from ckanext.edsnews.model import ckanextNews
from ckan.logic.validators import object_id_validators

Invalid = df.Invalid


def news_id_exists(value, context):

    session = context['session']

    result = session.query(ckanextNews).get(value)
    if not result:
        raise Invalid('%s: %s' % (_('Not found'), _('News')))
    return value


object_id_validators.update({
    'new news' : news_id_exists,
    'changed news' : news_id_exists
    })





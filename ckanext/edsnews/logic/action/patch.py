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

from ckan.plugins import toolkit
from ckan import logic
import ckan.lib.navl.dictization_functions as df

from ckanext.edsnews.logic import schema
from ckanext.edsnews.model import ckanextNews
from ckanext.edsnews.logic.dictization import news_dictize

log = logging.getLogger(__name__)


def news_patch(context, data_dict):
    '''Patch a news. See news_create for
    possible fields.

    The difference between the update and patch methods is that the patch will
    perform an update of the provided parameters, while leaving all other
    parameters unchanged, whereas the update method deletes all parameters
    not explicitly provided in the data_dict

    :param id: The id of the news.
    :type id: string

    :returns: a patched news
    :rtype: dictionary

    '''

    log.info('News patch: %r', data_dict)

    logic.check_access('news_patch', context, data_dict)

    news_patch_schema = schema.news_patch_schema()
    fields = news_patch_schema.keys()

    # Exclude fields from the schema that are not in data_dict
    for field in fields:
        if field not in data_dict.keys() and field != 'id':
            news_patch_schema.pop(field)

    data, errors = df.validate(data_dict, news_patch_schema,
                               context)

    if errors:
        raise toolkit.ValidationError(errors)

    news = ckanextNews.get(key=data['id'], attr='id')

    if news is None:
        raise logic.NotFound

    fields = news_patch_schema.keys()

    for field in fields:
        setattr(news, field, data.get(field))

        news.save()

    out = news_dictize(news)

    return out
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

from ckan import logic
from ckan.plugins import toolkit

from ckanext.edsnews.model import ckanextNews
from ckanext.edsnews.news_subscriptions_model import ckanextNewsSubscriptions

log = logging.getLogger(__name__)


def news_delete(context, data_dict):
    '''Delete news.

    :param id: the id of news
    :type id: string

    :rtype: dictionary

    '''

    logic.check_access('news_delete', context, data_dict)

    id = toolkit.get_or_bust(data_dict, 'id')

    ckanextNews.delete(id=id)

    log.info('News delete: %r', data_dict)
    return {
        'message': 'News successfully deleted'
    }

def news_subscription_delete(context, data_dict):
    '''Removes a subscription .

        :rtype: dictionary

        '''

    logic.check_access('news_subscription', context, data_dict)


    model = context['model']
    user = context['user']
    user_obj = model.User.get(user)

    ckanextNewsSubscriptions.unsubscribe(user_obj.id)

    return {
        'message': 'Subscription successfully removed'
    }
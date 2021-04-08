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

from ckan.plugins import toolkit
from ckan import logic
import ckan.lib.navl.dictization_functions as df

from ckanext.edsnews.logic import schema
from ckanext.edsnews.model import ckanextNews
from ckanext.edsnews.logic.dictization import news_dictize
from ckanext.edsnews.news_subscriptions_model import ckanextNewsSubscriptions

log = logging.getLogger(__name__)



def news_update(context, data_dict):
    '''Update a news. This will update all fields. See news_create for
    possible fields.

    :param id: The id of the news.
    :type id: string

    :returns: an updated news
    :rtype: dictionary

    '''

    log.info('News update: %r', data_dict)

    logic.check_access('news_update', context, data_dict)

    news_update_schema = schema.news_update_schema()

    data, errors = df.validate(data_dict, news_update_schema,
                               context)

    if errors:
        raise toolkit.ValidationError(errors)

    news = ckanextNews.get(key=data['id'], attr='id')

    if news is None:
        raise logic.NotFound

    news.title = data.get('title')
    news.content = data.get('content', u'')
    news.meta = data.get('meta', u'{}')
    news.expiration_date = data.get('expiration_date')
    news.image_url = data.get('image_url', u'')
    news.save()

    out = news_dictize(news)

    return out

def news_subscription_update(context, data_dict):
    '''Update a subscription .

        :param notify_by_mail: Setting if user should be notified by mail for news.
        :type notify_by_mail: boolean


        :returns: the updated subscription object
        :rtype: dictionary

        '''

    logic.check_access('news_subscription', context, data_dict)

    news_subscription_schema = schema.news_subscription_schema()

    data, errors = df.validate(data_dict, news_subscription_schema,
                               context)

    if errors:
        raise toolkit.ValidationError(errors)

    model = context['model']
    user = context['user']
    user_obj = model.User.get(user)

    notify_by_mail = data_dict.get('notify_by_mail', False)

    subscription = ckanextNewsSubscriptions.get_subscription(user_obj.id)

    if subscription is None:
        raise logic.NotFound

    subscription.notify_by_mail = notify_by_mail
    subscription.save()

    out = subscription.as_dict()
    return out
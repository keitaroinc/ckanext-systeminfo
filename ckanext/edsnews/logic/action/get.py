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
from operator import itemgetter

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

from ckan import logic
from ckan.plugins import toolkit

from ckanext.edsnews.model import ckanextNews
from ckanext.edsnews.logic.dictization import (
    news_dictize,
    news_list_dictize,
    news_subscriptions_dictize
)
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.activity_streams as activity_streams

#reguired to extend rendering of custom news activities
import ckanext.edsnews.logic.activity_streams as a_s

from ckanext.edsnews.news_subscriptions_model import ckanextNewsSubscriptions
from datetime import datetime
import ckanext.edsnews.helpers as helpers

log = logging.getLogger(__name__)


@toolkit.side_effect_free
def news_show(context, data_dict):
    '''Return the metadata of a news.

    :param id: the id of the news
    :type id: string

    :rtype: dictionary

    '''
    log.info('News show: %r', data_dict)

    id = toolkit.get_or_bust(data_dict, 'id')

    news = ckanextNews.get(key=id, attr='id')

    if news is None:
        raise logic.NotFound

    out = news_dictize(news)

    return out


@toolkit.side_effect_free
def news_list(context, data_dict):
    '''Return a list of created news ordered by date of creation (DESC) (defaults to 5).

    :param limit: limit the number of news to return (optional)
    :type id: int
    :param offset: offset  the results (defaults to 0)
    :type id: int

    :rtype: list of dictionaries

    '''
    log.info('News list: %r', data_dict)

    limit = data_dict.get('limit', 5)
    offset = data_dict.get('offset', 0)
    active_news = data_dict.get('active_news', False)

    if active_news:
        news_list = context['session'].query(ckanextNews)\
                        .filter(ckanextNews.expiration_date >= datetime.utcnow().date())\
                        .order_by(ckanextNews.created_at.desc()) \
                        .limit(limit).offset(offset).all()
    else:
        news_list = ckanextNews.search(limit=limit, offset=offset, order='created_at desc')

    cnt = context['session'].query(ckanextNews).count()

    out = {}
    out['news'] = news_list_dictize(news_list)
    out['count'] = cnt

    return out

def news_subscription_show(context, data_dict):
    '''Get subscription .

        :returns: subscription object if existing
        :rtype: dictionary

        '''

    logic.check_access('news_subscription', context, data_dict)

    model = context['model']
    user = context['user']
    user_obj = model.User.get(user)

    subscription = ckanextNewsSubscriptions.get_subscription(user_obj.id)

    if subscription:
        subscription = subscription.as_dict()
    else:
        subscription = None

    return subscription

def news_mail_subscribed_users_show(context, data_dict):
    '''Get all subscrtiptions for users that are subscribed for email notification also'''

    logic.check_access('news_mail_subscribed_users_show', context, data_dict)

    result = context['session'].query(ckanextNewsSubscriptions) \
        .filter(ckanextNewsSubscriptions.notify_by_mail == True).all()

    return news_subscriptions_dictize(result)


def dashboard_activity_list(context, data_dict):
    import ckan.model as model
    activity_dicts = logic.action.get.dashboard_activity_list(context, data_dict)
    is_subscribed = helpers.user_subscribed_to_news(context, data_dict)
    user_id = model.User.get(context['user']).id

    if is_subscribed:

        offset = data_dict.get('offset', 0)
        limit = int(
            data_dict.get('limit', config.get('ckan.activity_list_limit', 31)))

        news_activity_objects = model.Session.query(model.Activity) \
            .filter((model.Activity.activity_type == 'new news') | \
                    (model.Activity.activity_type == 'changed news')) \
            .limit(limit).offset(offset).all()

        news_activity_dicts = model_dictize.activity_list_dictize(
            news_activity_objects, context)

        # Mark the new (not yet seen by user) activities.
        strptime = datetime.strptime
        fmt = '%Y-%m-%dT%H:%M:%S.%f'
        last_viewed = model.Dashboard.get(user_id).activity_stream_last_viewed
        for activity in news_activity_dicts:
            if activity['user_id'] == user_id:
                # Never mark the user's own activities as new.
                activity['is_new'] = False
            else:
                activity['is_new'] = (
                    strptime(activity['timestamp'], fmt) > last_viewed)

        activity_dicts.extend(news_activity_dicts)
        activity_dicts = {v['id']: v for v in activity_dicts}.values()
        activity_dicts.sort(key=itemgetter('timestamp'), reverse=True)

    return activity_dicts


@logic.validate(logic.schema.default_pagination_schema)
def dashboard_activity_list_html(context, data_dict):
    '''Return the authorized (via login or API key) user's dashboard activity
       stream as HTML.

    The activity stream is rendered as a snippet of HTML meant to be included
    in an HTML page, i.e. it doesn't have any HTML header or footer.

    :param offset: where to start getting activity items from
        (optional, default: 0)
    :type offset: int
    :param limit: the maximum number of activities to return
        (optional, default: 31, the default value is configurable via the
        ckan.activity_list_limit setting)
    :type limit: int

    :rtype: string

    '''
    activity_stream = dashboard_activity_list(context, data_dict)
    model = context['model']
    offset = data_dict.get('offset', 0)
    extra_vars = {
        'controller': 'user',
        'action': 'dashboard',
        'offset': offset,
    }
    return activity_streams.activity_list_to_html(context, activity_stream,
                                                  extra_vars)
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

# -*- coding: utf-8 -
import re

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

import logging

import ckan.logic as l
import ckan.plugins.toolkit as t
import ckan.lib.navl.dictization_functions as df

from ckan.common import _
from ckan.lib.base import render_jinja2
from ckan.lib.helpers import render_markdown

from ckanext.edsnews.model import ckanextNews, gen_news_name
from ckanext.edsnews.news_subscriptions_model import ckanextNewsSubscriptions
from ckanext.edsnews.logic.dictization import news_dictize
from ckanext.edsnews.logic import schema
from ckanext.edsnews.emailer import send_email
from ckanext.edsnews.helpers import config_option_show

log = logging.getLogger(__name__)

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = df.validate
_check_access = l.check_access
_get_action = l.get_action
ValidationError = l.ValidationError
NotFound = l.NotFound
_get_or_bust = l.get_or_bust


def news_create(context, data_dict):
    '''Create a news.

    :param title: The title of the news.
    :type title: string

    :param description: Description of the news.
    :type description: string

    :param active: State of the news (optional). Default is true.
    :type active: boolean

    :param meta: Additional meta data for the news such as latitude/longitude etc.
    :type meta: string in JSON format

    :returns: the newly created news object
    :rtype: dictionary

    '''

    log.info('News create: %r', data_dict)
    l.check_access('news_create', context, data_dict)
    data, errors = df.validate(data_dict, schema.news_create_schema(),
                               context)

    if errors:
        raise t.ValidationError(errors)

    title = data.get('title')
    name = gen_news_name(title)
    content = data.get('content', u'')
    meta = data.get('meta', u'{}')
    expiration_date = data.get('expiration_date')
    image_url = data.get('image_url', u'')

    m = context.get('model')
    user_obj = m.User.get(context.get('user'))

    news = ckanextNews(title=title,
                       name=name,
                       content=content,
                       meta=meta,
                       expiration_date=expiration_date,
                       image_url=image_url,
                       creator_id=user_obj.id)
    news.save()
    out = news_dictize(news)

    # Send mail notification to all news subscribed users except the creator of the news
    # TODO: Email notifications should be sent asynchronous using celery tasks
    # TODO: Setup email server for testing mode
    send_email_condition = config.get('testing', False)
    if not send_email_condition:
        users = _get_action('news_mail_subscribed_users_show')(
            {'ignore_auth': True}, {}
        )
        vars = {'site_title_dk': config_option_show('ckan.site_title', 'da_DK'),
                'site_title_en': config_option_show('ckan.site_title', 'en'),
                'site_url': config.get('ckan.site_url'),
                'news_item_title': out['title'],
                'news_item_content': render_markdown(out['content'], True)}

        for u in users:
            if user_obj.id == u['subscriber_id']:
                continue

            u_obj = context['model'].User.get(u['subscriber_id'])
            if u_obj is None:
                continue

            vars['user_name'] = u_obj.name
            msg_body = render_jinja2('emails/news_published.txt', vars)
            msg_subject = render_jinja2('emails/news_published_subject.txt', vars)
            send_email(msg_body, u_obj.email, msg_subject)

    return out


def news_subscription_create(context, data_dict):
    '''Create a subscription .

        :param notify_by_mail: Setting if user should be notified by mail for news.
        :type notify_by_mail: boolean, default False

        :returns: the newly created subscription object
        :rtype: dictionary

        '''

    l.check_access('news_subscription', context, data_dict)
    news_subscription_schema = schema.news_subscription_schema()
    data, errors = df.validate(data_dict, news_subscription_schema,
                               context)

    if errors:
        raise t.ValidationError(errors)

    model = context['model']
    user = context['user']
    user_obj = model.User.get(user)

    notify_by_mail = data_dict.get('notify_by_mail', False)

    is_subscribed = ckanextNewsSubscriptions.get_subscription(user_obj.id)

    if is_subscribed:
        raise t.ValidationError('Subscribtion for user %s already exists!' % user_obj.name)

    subscription = ckanextNewsSubscriptions(subscriber_id=user_obj.id,
                                            notify_by_mail=notify_by_mail)
    subscription.save()
    out = subscription.as_dict()
    send_email_condition = config.get('testing', False)
    if not send_email_condition:
        # Notify the user via email
        # TODO: E-mail notifications should be sent asynchronous using celery tasks
        # TODO: Setup email server for testing mode
        vars = {'site_title_dk': config_option_show('ckan.site_title', 'da_DK'),
                'site_title_en': config_option_show('ckan.site_title', 'en'),
                'site_url': config.get('ckan.site_url'),
                'user_name': user_obj.name}
        msg_body = render_jinja2('emails/news_subscriptions.txt', vars)
        msg_subject = render_jinja2('emails/news_subscriptions_subject.txt', vars)
        send_email(msg_body, user_obj.email, msg_subject)

    return out

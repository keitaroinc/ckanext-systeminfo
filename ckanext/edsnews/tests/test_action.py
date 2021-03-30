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

from nose.tools import assert_raises
from datetime import datetime
from datetime import timedelta

from ckan.tests import helpers, factories
from ckan import plugins
from ckan import logic
from ckanext.edsnews.model import setup as setup_news_db
from ckanext.edsnews.news_subscriptions_model import setup_news_subscriptions

class ActionBase(object):
    @classmethod
    def setup_class(self):
        if not plugins.plugin_loaded('edsnews'):
            plugins.load('edsnews')

    def setup(self):
        helpers.reset_db()
        setup_news_db()
        setup_news_subscriptions()


    @classmethod
    def teardown_class(self):
        if plugins.plugin_loaded('edsnews'):
            plugins.unload('edsnews')


class TestEdsnewsActions(ActionBase):


    # NEWS tests
    def test_news_create_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        expiration_date = datetime.utcnow().date() + timedelta(days=1)
        data_dict = {
            'title': 'Test news',
            'content': 'Test content',
            'expiration_date': str(expiration_date),
            'image_url': ''
        }

        result = helpers.call_action('news_create',
                                     context=context, **data_dict)

        assert result['title'] == data_dict['title']
        assert result['content'] == data_dict['content']
        assert result['expiration_date'] == data_dict['expiration_date']
        assert result['image_url'] == data_dict['image_url']

        helpers.call_action('news_delete',
                            context=context, id=result['id'])


    def test_news_create_missing_values(self):
        # 'title' and 'expiration_date' are required values

        user = factories.Sysadmin()
        context = {'user': user['name']}

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_create',
                      context=context)

    def test_news_create_invalid_values(self):
        # 'expiration_date' must be in ISO format

        user = factories.Sysadmin()
        context = {'user': user['name']}

        data_dict = {
            'title': 'Test news',
            'expiration_date': '2017'
        }

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_create',
                      context=context,
                      **data_dict)


    def test_news_create_expiration_date_in_past(self):
        # 'expiration_date' must be in future

        user = factories.Sysadmin()
        context = {'user': user['name']}
        expiration_date = datetime.utcnow().date() - timedelta(days=1)

        data_dict = {
            'title': 'Test news',
            'expiration_date': str(expiration_date)
        }

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_create',
                      context=context,
                      **data_dict)


    def test_news_delete_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        expiration_date = datetime.utcnow().date() + timedelta(days=1)
        data_dict = {
            'title': 'Test news',
            'content': 'Test content',
            'expiration_date': str(expiration_date),
            'image_url': ''
        }

        result = helpers.call_action('news_create',
                                     context=context, **data_dict)

        news_id = result['id']

        data_dict = {
            'id': news_id
        }

        result = helpers.call_action('news_delete',
                                     context=context, **data_dict)

        assert result['message'] == 'News successfully deleted'


    def test_news_delete_news_not_found(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        data_dict = {
            'id': 'invalid_id'
        }

        assert_raises(logic.NotFound,
                      helpers.call_action,
                      'news_delete',
                      context=context,
                      **data_dict)

    def test_news_delete_missing_id(self):
        # 'id' is a required value

        user = factories.Sysadmin()
        context = {'user': user['name']}

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_delete',
                      context=context)

    def test_news_show_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        expiration_date = datetime.utcnow().date() + timedelta(days=1)
        data_dict_create = {
            'title': 'Test news',
            'content': 'Test content',
            'expiration_date': str(expiration_date),
            'image_url': ''
        }

        result = helpers.call_action('news_create',
                                     context=context, **data_dict_create)

        news_id = result['id']

        data_dict = {
            'id': news_id
        }

        result = helpers.call_action('news_show',
                                     context=context, **data_dict)

        assert result['title'] == data_dict_create['title']
        assert result['content'] == data_dict_create['content']
        assert result['expiration_date'].split(" ")[0] == data_dict_create['expiration_date']


    def test_news_show_missing_id(self):
        # 'id' is a required value

        user = factories.Sysadmin()
        context = {'user': user['name']}

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_show',
                      context=context)


    def test_news_show_news_not_found(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        data_dict = {
            'id': 'invalid_id'
        }

        assert_raises(logic.NotFound,
                      helpers.call_action,
                      'news_show',
                      context=context,
                      **data_dict)


    def test_news_list_empty(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}

        result = helpers.call_action('news_list',
                                     context=context)

        assert len(result['news']) == 0


    def test_news_list_with_single_news(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        expiration_date = datetime.utcnow().date() + timedelta(days=1)
        data_dict = {
            'title': 'Test news',
            'content': 'Test content',
            'expiration_date': str(expiration_date),
            'image_url': ''
        }

        helpers.call_action('news_create',
                             context=context, **data_dict)

        result = helpers.call_action('news_list',
                                     context=context)

        assert len(result['news']) == 1
        news = result['news']
        assert news[0]['title'] == data_dict['title']
        assert news[0]['content'] == data_dict['content']
        assert news[0]['expiration_date'].split(" ")[0] == data_dict['expiration_date']


    def test_news_list_with_ten_news(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        expiration_date = datetime.utcnow().date() + timedelta(days=1)
        data_dict = {
            'title': 'Test news',
            'content': 'Test content',
            'expiration_date': str(expiration_date),
            'image_url': ''
        }

        # Create 10 news
        for i in range(10):
            helpers.call_action('news_create',
                                context=context, **data_dict)

        result = helpers.call_action('news_list',
                                     context=context)

        # If 'limit' is not specified, the default is the last 5 created news
        assert len(result['news']) == 5

        result = helpers.call_action('news_list',
                                     context=context, limit=8)

        assert len(result['news']) == 8


    def test_news_patch_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        expiration_date = datetime.utcnow().date() + timedelta(days=1)
        data_dict_create = {
            'title': 'Test news',
            'content': 'Test content',
            'expiration_date': str(expiration_date),
            'image_url': ''
        }

        result = helpers.call_action('news_create',
                                     context=context, **data_dict_create)

        news_id = result['id']

        data_dict_patch = {
            'id': news_id,
            'title': 'News patch title'
        }

        result = helpers.call_action('news_patch',
                                     context=context, **data_dict_patch)

        assert result['title'] == data_dict_patch['title']
        assert result['content'] == data_dict_create['content']
        assert result['expiration_date'].split(" ")[0] == data_dict_create['expiration_date']


    def test_news_patch_missing_id(self):
        # 'id' is a required value

        user = factories.Sysadmin()
        context = {'user': user['name']}

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_patch',
                      context=context)


    def test_news_patch_news_not_found(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        data_dict = {
            'id': 'invalid_id'
        }

        assert_raises(logic.NotFound,
                      helpers.call_action,
                      'news_patch',
                      context=context,
                      **data_dict)


    def test_news_update_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        expiration_date = datetime.utcnow().date() + timedelta(days=1)
        data_dict = {
            'title': 'Test news',
            'content': 'Test content',
            'expiration_date': str(expiration_date),
            'image_url': ''
        }

        result = helpers.call_action('news_create',
                                     context=context, **data_dict)

        news_id = result['id']

        data_dict = {
            'id': news_id,
            'title': 'Test news update',
            'content': 'Test content update',
            'expiration_date': str(expiration_date + timedelta(days=1))
        }

        result = helpers.call_action('news_update',
                                     context=context, **data_dict)

        assert result['title'] == data_dict['title']
        assert result['content'] == data_dict['content']
        assert result['expiration_date'].split(" ")[0] == data_dict['expiration_date']


    def test_news_update_missing_values(self):
        # 'id' , 'title' and 'expiration_date' are required values

        user = factories.Sysadmin()
        context = {'user': user['name']}

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_update',
                      context=context)

    def test_news_update_invalid_values(self):
        # 'expiration_date' must be in ISO format
        user = factories.Sysadmin()
        context = {'user': user['name']}
        expiration_date = datetime.utcnow().date() + timedelta(days=1)
        data_dict = {
            'title': 'Test news',
            'content': 'Test content',
            'expiration_date': str(expiration_date),
            'image_url': ''
        }

        result = helpers.call_action('news_create',
                                     context=context, **data_dict)

        news_id = result['id']

        data_dict = {
            'id': news_id,
            'title': 'Test news update',
            'content': 'Test content update',
            'expiration_date': '2017'
        }


        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_update',
                      context=context,
                      **data_dict)


    #NEWS SUBSCRIPTIONS tests
    def test_news_subscription_create_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        data_dict = {
            'notify_by_mail': True,
        }

        result = helpers.call_action('news_subscription_create',
                                     context=context, **data_dict)

        assert result['subscriber_id'] == user['id']
        assert result['notify_by_mail'] == data_dict['notify_by_mail']

        helpers.call_action('news_subscription_delete',
                            context=context)


    def test_news_subscription_create_missing_values(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_subscription_create',
                      context=context)

    def test_news_subscription_create_invalid_values(self):
        # 'notify_by_mail' must be type boolean
        user = factories.Sysadmin()
        context = {'user': user['name']}

        data_dict = {
            'notify_by_mail': 'invalid_value',
        }

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_subscription_create',
                      context=context,
                      **data_dict)


    def test_news_subscription_delete_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        data_dict = {
            'notify_by_mail': True,
        }

        result = helpers.call_action('news_subscription_create',
                                     context=context, **data_dict)

        assert result['subscriber_id'] == user['id']
        assert result['notify_by_mail'] == data_dict['notify_by_mail']

        result = helpers.call_action('news_subscription_delete',
                            context=context)

        assert result['message'] == 'Subscription successfully removed'


    def test_news_subscription_delete_not_found(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}

        assert_raises(logic.NotFound,
                      helpers.call_action,
                      'news_subscription_delete',
                      context=context)


    def test_news_subscription_show_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        data_dict = {
            'notify_by_mail': False,
        }

        helpers.call_action('news_subscription_create',
                            context=context, **data_dict)

        result = helpers.call_action('news_subscription_show',
                                     context=context)

        assert result['subscriber_id'] == user['id']
        assert result['notify_by_mail'] == data_dict['notify_by_mail']

        helpers.call_action('news_subscription_delete',
                            context=context)


    def test_news_subscription_show_not_found(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}

        result = helpers.call_action('news_subscription_show',
                            context=context)
        assert result == None




    def test_news_subscription_update_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        data_dict = {
            'notify_by_mail': False,
        }

        helpers.call_action('news_subscription_create',
                            context=context, **data_dict)

        data_dict = {
            'notify_by_mail': True,
        }

        result = helpers.call_action('news_subscription_update',
                                     context=context, **data_dict)

        assert result['subscriber_id'] == user['id']
        assert result['notify_by_mail'] == data_dict['notify_by_mail']

        helpers.call_action('news_subscription_delete',
                            context=context)


    def test_news_subscription_update_not_found(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}

        data_dict = {
            'notify_by_mail': True,
        }

        assert_raises(logic.NotFound,
                      helpers.call_action,
                      'news_subscription_update',
                      context=context, **data_dict)


    def test_news_subscription_update_invalid_value(self):
        # 'notify_by_mail' must be type boolean
        user = factories.Sysadmin()
        context = {'user': user['name']}

        data_dict = {
            'notify_by_mail': 'invalid_value',
        }

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_subscription_update',
                      context=context, **data_dict)


    def test_news_subscription_update_missing_value(self):
        # 'notify_by_mail' is required parameter
        user = factories.Sysadmin()
        context = {'user': user['name']}

        assert_raises(logic.ValidationError,
                      helpers.call_action,
                      'news_subscription_update',
                      context=context)



    def test_news_mail_subscribed_users_show_valid(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}
        data_dict = {
            'notify_by_mail': True,
        }

        helpers.call_action('news_subscription_create',
                                     context=context, **data_dict)

        result = helpers.call_action('news_mail_subscribed_users_show',
                            context=context)

        assert len(result) == 1


    def test_news_mail_subscribed_users_show_no_subscriptions(self):
        user = factories.Sysadmin()
        context = {'user': user['name']}

        result = helpers.call_action('news_mail_subscribed_users_show',
                            context=context)

        assert result == []

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
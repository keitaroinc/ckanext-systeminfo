import ckan.model as m


def news_dictize(obj):
    out = obj.as_dict()

    creator = m.User.get(out['creator_id'])
    out['creator'] = creator.name
    del out['creator_id']
    return out


def news_list_dictize(list_of_dict):
    news_list = []

    for obj in list_of_dict:
        news_list.append(news_dictize(obj))

    return news_list

def news_subscriptions_dictize(list):
    result = []

    for obj in list:
        result.append(obj.as_dict())

    return result



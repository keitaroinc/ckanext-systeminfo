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



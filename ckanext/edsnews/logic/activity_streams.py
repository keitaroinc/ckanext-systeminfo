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

# encoding: utf-8

from webhelpers.html import literal

from ckan.lib.activity_streams import (
                    activity_snippet_functions,
                    activity_stream_string_functions,
                    activity_stream_string_icons
)
import ckanext.edsnews.helpers as helpers

from ckan.common import _


def get_snippet_news(activity, detail):
    data = activity['data']
    link = helpers.news_link(data) if data else ''
    return literal('''<span>%s</span>'''
                   % (link)
                   )

def activity_stream_string_changed_news(context, activity):
    return _("{actor} updated the news {news}")

def activity_stream_string_new_news(context, activity):
    return _("{actor} created the news {news}")


# A dictionary mapping activity snippets to functions that expand the snippets.
activity_snippet_functions.update({'news': get_snippet_news})

# A dictionary mapping activity types to functions that return translatable
# string descriptions of the activity types.
activity_stream_string_functions.update({
  'changed news': activity_stream_string_changed_news,
  'new news': activity_stream_string_new_news

})

# A dictionary mapping activity types to the icons associated to them
activity_stream_string_icons.update({
  'changed news': 'newspaper-o',
  'new news': 'newspaper-o'
})


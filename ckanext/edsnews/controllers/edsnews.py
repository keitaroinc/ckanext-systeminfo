import json
import logging

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

from ckan.lib import base
from ckan.plugins import toolkit
from ckan import model, logic
from ckan.common import c, _, request
import ckan.lib.helpers as h
import ckan.plugins as p

from ckanext.edsnews.emailer import send_email
import ckanext.edsnews.helpers as helpers

log = logging.getLogger(__name__)
redirect = toolkit.redirect_to


def _get_context():
    return {
        'model': model,
        'session': model.Session,
        'user': c.user or c.author,
        'auth_user_obj': c.userobj
    }


def _get_action(action, data_dict):
    return toolkit.get_action(action)(_get_context(), data_dict)


class EdsnewsController(base.BaseController):
    def __get_page_number(self, params):
        if p.toolkit.check_ckan_version(min_version='2.5.0', max_version='2.5.10'):
            return self._get_page_number(params)
        return h.get_page_number(params)

    def news_create(self, fields=None, errors=None):

        if request.method.lower() == 'post' and not fields:
            fields = dict(toolkit.request.POST)
            try:
                junk = _get_action('news_create', fields)

                activity_dict = {
                    'user_id': c.userobj.id,
                    'object_id': junk['id'],
                    'activity_type': 'new news',
                    'data': junk
                }
                activity_junk = _get_action('activity_create', activity_dict)

            except toolkit.ValidationError, e:
                errors = e.error_dict
                return self.news_create(fields, errors)

            h.flash_success(_('The news was created successfully.'))
            redirect(h.url_for('news_index'))

        if not fields:
            fields = {}
        errors = errors or {}

        extra_vars = {
            'data': fields,
            'errors': errors
        }

        return toolkit.render('edsnews/news_create.html', extra_vars=extra_vars)

    def news_update(self, id, fields=None, errors=None):

        news = _get_action('news_show', {'id': id})

        if request.method.lower() == 'post' and not fields:
            fields = dict(toolkit.request.POST)
            fields['id'] = id

            try:
                junk = _get_action('news_update', fields)

                activity_dict = {
                    'user_id': c.userobj.id,
                    'object_id': junk['id'],
                    'activity_type': 'changed news',
                    'data': junk
                }
                activity_junk = _get_action('activity_create', activity_dict)

            except toolkit.ValidationError, e:
                errors = e.error_dict
                return self.news_update(id, fields, errors)

            h.flash_success(_('The news was updated successfully.'))
            redirect(h.url_for('news_show', id=id))

        if not fields:
            fields = news
            fields['id'] = id
        errors = errors or {}
        news_current_title = news.get('title')

        extra_vars = {
            'data': fields,
            'errors': errors,
            'news_current_title': news_current_title
        }
        return toolkit.render('edsnews/news_update.html', extra_vars)

    def news_index(self):

        page = self.__get_page_number(request.params)
        limit = int(config.get('ckanext.edsnews.news_show_limit', 10))
        pagination_limit = int(config.get('ckanext.edsnews.pagination_limit', 5))
        c.page = page
        c.limit = limit
        c.pagination_limit = pagination_limit
        offset = (page - 1) * limit if page > 1 else 0
        data = _get_action('news_list', {'limit': limit, 'offset': offset})
        c.total = data['count']
        extra_vars = {
            'news_list': data['news']
        }

        return toolkit.render('edsnews/news_list.html', extra_vars)

    def news_show(self, id):
        try:
            news = _get_action('news_show', {'id': id})
        except (logic.ValidationError, logic.NotFound):
            toolkit.abort(404, _('News not found'))

        extra_vars = {
            'news': news
        }
        return toolkit.render('edsnews/news_page.html', extra_vars)

    def news_delete(self, id):

        _get_action('news_delete', {'id': id})
        h.flash_success(_('News was removed successfully.'))
        redirect(h.url_for('news_index'))

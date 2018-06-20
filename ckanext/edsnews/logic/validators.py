import ckan.lib.navl.dictization_functions as df

from ckan.common import _
from ckanext.edsnews.model import ckanextNews
from ckan.logic.validators import object_id_validators

Invalid = df.Invalid


def news_id_exists(value, context):

    session = context['session']

    result = session.query(ckanextNews).get(value)
    if not result:
        raise Invalid('%s: %s' % (_('Not found'), _('News')))
    return value


object_id_validators.update({
    'new news' : news_id_exists,
    'changed news' : news_id_exists
    })





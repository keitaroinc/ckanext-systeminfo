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
import datetime
import uuid

import ckan.model as m
import ckan.logic as l
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import types
from sqlalchemy import Index

from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.exc import NoSuchTableError
from ckan.model.meta import metadata, mapper, Session
from ckan.model.types import make_uuid
from ckan.model.domain_object import DomainObject
from ckan.lib.munge import munge_title_to_name

log = logging.getLogger(__name__)

__all__ = [
    'ckanextNews', 'news_table',
]

news_table = None


def setup():
    if news_table is None:
        define_news_tables()
        log.debug('News table defined in memory')

        if not news_table.exists():
            news_table.create()

    else:
        log.debug('News table already exist')
        from ckan.model.meta import engine
        inspector = Inspector.from_engine(engine)

        try:
            inspector.get_indexes("ckanext_news")
        except NoSuchTableError:
            news_table.create()

        index_names = [index['name'] for index in inspector.get_indexes("ckanext_news")]
        if not "ckanext_news_id_idx" in index_names:
            log.debug('Creating index for ckanext_news')
            Index("ckanext_news_id_idx", news_table.c.ckanext_news_id).create()
            Index("ckanext_news_name_idx", news_table.c.ckanext_news_name).create()


class ckanextNews(DomainObject):
    '''Convenience methods for searching objects
    '''
    key_attr = 'id'

    @classmethod
    def get(cls, key, default=None, attr=None):
        '''Finds a single entity in the register.'''
        if attr is None:
            attr = cls.key_attr
        kwds = {attr: key}
        o = Session.query(cls).autoflush(False)
        o = o.filter_by(**kwds).first()
        if o:
            return o
        else:
            return default

    @classmethod
    def search(cls, limit, offset=0, order='id', **kwds):
        query = Session.query(cls).autoflush(False)
        query = query.filter_by(**kwds)
        query = query.order_by(order)
        query = query.limit(limit).offset(offset)
        return query.all()

    @classmethod
    def delete(cls, id):
        # Delete single event
        obj = Session.query(cls).filter_by(id=id).first()
        if not obj:
            raise l.NotFound

        Session.delete(obj)
        Session.commit()


def define_news_tables():
    global news_table
    news_table = Table('ckanext_news', metadata,
                        Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
                        Column('name', types.UnicodeText, nullable=False, unique=True),
                        Column('title', types.UnicodeText, nullable=False),
                        Column('content', types.UnicodeText, default=u''),
                        # SQLAlchemy 0.9 doesn't support JSON type
                        Column('meta', types.UnicodeText, default=u'{}'),
                        Column('expiration_date', types.DateTime, nullable=False),
                        Column('creator_id', types.UnicodeText, nullable=False),
                        Column('image_url', types.UnicodeText, default=u''),
                        Column('created_at', types.DateTime, default=datetime.datetime.utcnow),
                        Index('ckanext_news_id_idx', 'id'),
                        Index('ckanext_news_name_idx', 'name'))

    mapper(
        ckanextNews,
        news_table
    )


def gen_news_name(title):
    name = munge_title_to_name(title).replace('_', '-')
    while '--' in name:
        name = name.replace('--', '-')
    news_obj = Session.query(ckanextNews).filter(ckanextNews.name == name).first()
    if news_obj:
        return name + str(uuid.uuid4())[:5]

    return name

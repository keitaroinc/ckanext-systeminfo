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

log = logging.getLogger(__name__)

__all__ = [
    'ckanextNewsSubscriptions', 'news_subscriptions_table',
]

news_subscriptions_table = None


def setup_news_subscriptions():
    if news_subscriptions_table is None:
        define_news_subscriptions_tables()
        log.debug('News subscriptions table defined in memory')

        if not news_subscriptions_table.exists():
            news_subscriptions_table.create()

    else:
        log.debug('News subscriptions table already exist')
        from ckan.model.meta import engine
        inspector = Inspector.from_engine(engine)

        try:
            inspector.get_indexes("news_subscriptions_table")
        except NoSuchTableError:
            news_subscriptions_table.create()

        index_names = [index['name'] for index in inspector.get_indexes("news_subscriptions_table")]
        if not "ckanext_news_subscription_id_idx" in index_names:
            log.debug('Creating index for ckanext_news_subscriptions')
            Index("ckanext_news_subscription_id_idx", news_subscriptions_table.c.ckanext_news_subscription_id).create()


class ckanextNewsSubscriptions(DomainObject):
    '''Convenience methods for searching objects
    '''

    @classmethod
    def get_subscription(cls, subscriber_id):

        kwds = {'subscriber_id': subscriber_id}
        o = Session.query(cls).autoflush(False)
        o = o.filter_by(**kwds).first()
        if o:
            return o
        else:
            return None

    @classmethod
    def unsubscribe(cls, subscriber_id):
        # unsubscribe user from news feed
        obj = Session.query(cls).filter_by(subscriber_id=subscriber_id).first()
        if not obj:
            raise l.NotFound
        Session.delete(obj)
        Session.commit()


def define_news_subscriptions_tables():
    global news_subscriptions_table
    news_subscriptions_table = Table('news_subscriptions_table', metadata,
                        Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
                        Column('subscriber_id', types.UnicodeText, nullable=False, unique=True),
                        Column('notify_by_mail', types.Boolean, default=False),
                        Column('datetime', types.DateTime, default=datetime.datetime.utcnow),
                        Index('ckanext_news_subscription_id_idx', 'id'))

    mapper(
        ckanextNewsSubscriptions,
        news_subscriptions_table
    )
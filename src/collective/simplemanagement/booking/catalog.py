#-*- coding: utf-8 -*-

from zope.interface import implementer
from zope.container.contained import Contained

from zope.catalog.catalog import Catalog
from zope.catalog.interfaces import ICatalogIndex
from zope.catalog.attribute import AttributeIndex
from zope.index import field
from zope.index import text
from zope.index import keyword

from ..interfaces import IBooking


@implementer(ICatalogIndex)
class TextIndex(AttributeIndex, text.TextIndex, Contained):
    pass


@implementer(ICatalogIndex)
class KeywordIndex(AttributeIndex, keyword.KeywordIndex, Contained):
    pass


@implementer(ICatalogIndex)
class FieldIndex(AttributeIndex, field.FieldIndex, Contained):
    pass


def setup_catalog():
    catalog = Catalog()
    catalog['date'] = FieldIndex(
        'date',
        IBooking,
        False
    )
    catalog['text'] = TextIndex(
        'text',
        IBooking,
        False
    )
    catalog['owner'] = TextIndex(
        'owner',
        IBooking,
        False
    )
    # catalog['references'] = FieldIndex(
    #     'references',
    #     IBooking,
    #     False
    # )
    # catalog['tags'] = KeywordIndex(
    #     'tags',
    #     IBooking,
    #     True
    # )
    return catalog


def prepare_query(catalog, query):
    """ prepare query for catalog search
    """
    catalog_query = {}
    for key, value in query.iteritems():
        if isinstance(catalog[key], FieldIndex) and \
                not isinstance(value, (tuple, list)):
            value = (value, value)
        catalog_query[key] = value
    return catalog_query

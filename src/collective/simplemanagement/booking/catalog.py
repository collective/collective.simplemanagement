#-*- coding: utf-8 -*-

from zope.interface import implementer
from zope.container.contained import Contained

from zope.catalog.catalog import Catalog
from zope.catalog.interfaces import ICatalogIndex
from zope.catalog.attribute import AttributeIndex
from zope.index import field
from zope.index import text

from ..interfaces import IBooking


@implementer(ICatalogIndex)
class TextIndex(AttributeIndex, text.TextIndex, Contained):
    pass


@implementer(ICatalogIndex)
class FieldIndex(AttributeIndex, field.FieldIndex, Contained):
    pass


def setup_catalog():
    catalog = Catalog()
    catalog['date'] = FieldIndex(
        'date',
        IBooking,
        True
    )
    catalog['text'] = TextIndex(
        'text',
        IBooking,
        True
    )
    catalog['owner'] = TextIndex(
        'owner',
        IBooking,
        True
    )
    catalog['references'] = FieldIndex(
        'owner',
        IBooking,
        True
    )
    catalog['tags'] = FieldIndex(
        'owner',
        IBooking,
        True
    )
    return catalog

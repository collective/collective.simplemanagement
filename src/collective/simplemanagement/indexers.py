#-*- coding: utf-8 -*-

from DateTime import DateTime
from plone.indexer.decorator import indexer
from plone.uuid.interfaces import IUUID

from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName

from .interfaces import IIteration
from .interfaces import IEpic
from .interfaces import IStory
from .interfaces import IProject
from .interfaces import IOrderNumber


@indexer(IIteration)
def start(obj):
    return DateTime(obj.start.isoformat())


@indexer(IIteration)
def end(obj):
    return DateTime(obj.end.isoformat())


def SearchableText(obj, text=False):
    text = [obj.getId(), obj.Title()]
    description = obj.Description()
    if description:
        text.append(description)
    return text


@indexer(IProject)
def SearchableText_project(obj):
    searchable = SearchableText(obj)
    if obj.notes is not None or obj.notes.output is None:
        searchable.append(obj.notes.output)

    if obj.customer is not None:
        searchable.append(obj.customer)

    if obj.classifiers:
        searchable.append(' '.join(obj.classifiers))

    return ' '.join(searchable)


@indexer(IIteration)
def SearchableText_iteration(obj):
    searchable = SearchableText(obj)
    return ' '.join(searchable)


@indexer(IStory)
def SearchableText_story(obj):
    searchable = SearchableText(obj)
    if obj.text is not None:
        searchable.append(obj.text)
    return ' '.join(searchable)


@indexer(IEpic)
def SearchableText_epic(obj):
    searchable = SearchableText(obj)
    text = obj.get_text()
    if text is not None:
        searchable.append(text)
    return ' '.join(searchable)


@indexer(IContentish)
def order_number(obj):
    if IOrderNumber.providedBy(obj):
        # Store index value in lowercase
        order_n = obj.order_number
        if order_n:
            order_n = order_n.lower()
        return order_n
    raise AttributeError


@indexer(IContentish)
def short_uuid(obj):
    uuid = IUUID(obj, None)
    if uuid is not None:
        portal_catalog = getToolByName(obj, 'portal_catalog')
        short_uuids = portal_catalog.uniqueValuesFor('short_uuid')
        uuid = uuid.replace('-', '')
        for i in xrange(0, 32):
            short_uuid_ = uuid[:i]
            if short_uuid_ in short_uuids:
                same_short = portal_catalog.searchResults(
                    short_uuid=short_uuid_
                )
                if same_short[0]['UID'] == uuid:
                    return short_uuid_
            else:
                return short_uuid_
    return uuid

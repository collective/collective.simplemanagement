from DateTime import DateTime
from plone.indexer.decorator import indexer

from .interfaces import IIteration
from .interfaces import IEpic
from .interfaces import IStory
from .interfaces import IProject
from .interfaces import IBooking


@indexer(IIteration)
def start(obj):
    return DateTime(obj.start.isoformat())


@indexer(IIteration)
def end(obj):
    return DateTime(obj.end.isoformat())


@indexer(IBooking)
def date(obj):
    return DateTime(obj.date.isoformat())


def SearchableText(obj, text=False):
    text = [obj.id, obj.title]
    if obj.description:
        text.append(obj.description)
    return ' '.join(text)


@indexer(IProject)
def SearchableText_project(obj):
    searchable = [SearchableText(obj)]
    if obj.notes is not None or obj.text.output is None:
        searchable.append(obj.notes.output)

    if obj.customer is not None:
        searchable.append(obj.customer)

    if obj.classifiers:
        searchable.append(' '.join(obj.classifiers))

    return ' '.join(searchable)


@indexer(IIteration)
def SearchableText_iteration(obj):
    return SearchableText(obj)


@indexer(IStory)
def SearchableText_story(obj):
    if obj.text is None:
        return SearchableText(obj)
    return ' '.join((SearchableText(obj), obj.text))


@indexer(IEpic)
def SearchableText_epic(obj):
    if obj.text is None or obj.text.output is None:
        return SearchableText(obj)
    return ' '.join((SearchableText(obj), obj.text.output))

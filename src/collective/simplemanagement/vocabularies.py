from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from .configure import STATUS_ITEMS
from .configure import ENV_TYPES
from .configure import ROLES
from .utils import get_project


class baseVocabulary(object):
    implements(IVocabularyFactory)
    terms = []

    def __call__(self, context):
        terms = []
        for term in self.terms:
            terms.append(SimpleVocabulary.createTerm(term[0],
                                                     term[0],
                                                     term[1]))

        return SimpleVocabulary(terms)


class statusVocab(baseVocabulary):
    terms = STATUS_ITEMS


class envtypesVocab(baseVocabulary):
    terms = ENV_TYPES


class rolesVocab(baseVocabulary):
    terms = ROLES


class milestonesVocab(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        project = get_project(context)
        terms = []
        if project is not None:
            for milestone in project.milestones:
                terms.append(
                    SimpleVocabulary.createTerm(milestone.getId(),
                                                milestone.getId(),
                                                milestone.name))
        return SimpleVocabulary(terms)

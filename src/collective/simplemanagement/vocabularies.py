from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from .configure import Settings
from .utils import get_project


class baseVocabulary(object):
    implements(IVocabularyFactory)
    terms_attribute = ''

    @property
    def terms(self):
        settings = Settings()
        return getattr(settings, self.terms_attribute)

    def __call__(self, context):
        terms = []
        for term in self.terms:
            terms.append(SimpleVocabulary.createTerm(term[0],
                                                     term[0],
                                                     term[1]))

        return SimpleVocabulary(terms)


class statusVocab(baseVocabulary):

    terms_attribute = 'statuses'


class envtypesVocab(baseVocabulary):

    terms_attribute = 'env_types'


class rolesVocab(baseVocabulary):

    terms_attribute = 'resource_roles'


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

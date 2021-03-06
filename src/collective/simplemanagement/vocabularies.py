from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from plone.app.vocabularies.users import UsersVocabulary
import plone.api

from Products.CMFCore.utils import getToolByName

from .configure import Settings
from . import api


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


class offDutyReasonsVocab(baseVocabulary):

    terms_attribute = 'off_duty_reasons'


class milestonesVocab(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        project = api.content.get_project(context)
        terms = []
        if project is not None:
            if project.milestones:
                for milestone in project.milestones:
                    terms.append(
                        SimpleVocabulary.createTerm(
                            milestone.name.encode('utf-8'),
                            milestone.name.encode('utf-8'),
                            milestone.name
                        )
                    )
        return SimpleVocabulary(terms)


class classifiersVocab(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        catalog = getToolByName(context, 'portal_catalog')
        terms = []
        for term in catalog.uniqueValuesFor('classifiers'):
            terms.append(
                SimpleVocabulary.createTerm(term, term, term)
            )

        return SimpleVocabulary(terms)


class iterationsVocab(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        project = api.content.get_project(context)
        terms = []
        catalog = getToolByName(context, 'portal_catalog')
        if project is not None:
            res = catalog.search({
                'path': '/'.join(project.getPhysicalPath()),
                'portal_type': 'Iteration'
            })

            for term in res:
                path = term.getPath()
                terms.append(
                    SimpleVocabulary.createTerm(
                        path, path, term.Title)
                )
        return SimpleVocabulary(terms)


class UsersFactory(object):
    """
    """
    implements(IVocabularyFactory)

    def __call__(self, context, query=''):
        # we get z3c.form.interfaces.NO_VALUE
        # or Resource istance or dicts into `context`
        # let's make sure we always get something  that's acquisition aware
        context = plone.api.portal.get()
        acl_users = getToolByName(context, "acl_users")
        users = sorted(acl_users.searchUsers(fullname=query),
                       key=lambda x: x['title'])
        return UsersVocabulary(users, context)

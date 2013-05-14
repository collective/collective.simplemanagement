from Acquisition import aq_inner
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from ..utils import get_project
from .. import messageFactory as _


class IProjectPortlet(IPortletDataProvider):
    """A portlet which shows the available project actions.
    """


class Assignment(base.Assignment):
    implements(IProjectPortlet)

    title = _(u'Project')


class Renderer(base.Renderer):

    @property
    def helpers(self):
        helpers = self.context.restrictedTraverse('@@sm_helpers')
        return helpers

    @property
    def available(self):
        return self._project is not None \
            and self.helpers.has_sm_actions()

    @property
    def _project(self):
        return get_project(aq_inner(self.context))

    def actions(self):
        return self.helpers.sm_actions(project=self._project)

    render = ViewPageTemplateFile('project.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()

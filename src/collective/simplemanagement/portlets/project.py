from plone.portlets.interfaces import IPortletDataProvider
from plone.app.i18n.locales.browser.selector import LanguageSelector
from zope.component import getMultiAdapter
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.utils import getToolByName

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
    def available(self):
        return self._project is not None and self._actions()

    @property
    def _project(self):
        return get_project(self.context)

    def _actions(self):
        pa = getToolByName(self.context, 'portal_actions')
        return pa.simplemanagement_actions.values()

    def actions(self):
        project_url = self._project.absolute_url()
        expr_context = getExprContext(self.context)
        for i in self._actions():
            yield {
                'title': i.title,
                'id': i.id,
                'url': '/'.join((
                    project_url,
                    i.url_expr_object(expr_context)
                )),
                'description': i.description
            }

    render = ViewPageTemplateFile('project.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()

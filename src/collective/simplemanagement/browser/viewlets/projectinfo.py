from urllib import unquote
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common as base

from collective.simplemanagement.utils import get_project


class ProjectInfo(base.ViewletBase):

    index = ViewPageTemplateFile('templates/projectinfo.pt')

    def update(self):
        base.ViewletBase.update(self)
        self.project = get_project(self.context)

    def available(self):
        return self.project is not None

    @property
    def info(self):
        if not self.project:
            return

        cs = self.context.restrictedTraverse('plone_context_state')
        is_project = self.context is self.project and cs.is_view_template()

        return {
            'is_project': is_project,
            'project_url': self.project.absolute_url(),
            'project_title': self.project.Title()
        }

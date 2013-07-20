from urllib import unquote
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common as base

from collective.simplemanagement.configure import DOCUMENTS_ID, TRACKER_ID
from collective.simplemanagement.utils import get_project
from collective.simplemanagement import _


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

    def buttons(self):
        info = self.info
        buttons = [
            {
                'url': "%s/@@dashboard" % info['project_url'],
                'title': _(u'Dashboard')
            },
            {
                'url': "%s/@@alliterations" % info['project_url'],
                'title': _(u'Iterations')
            },
            {
                'url': "%s/@@backlog" % info['project_url'],
                'title': _(u'Backlog')
            },
            {
                'url': "%s/@@worklog" % info['project_url'],
                'title': _(u'Worklog')
            },
            {
                'url': "%s/@@planning" % info['project_url'],
                'title': _(u'Planning')
            },
            {
                'url': "%s/@@report" % info['project_url'],
                'title': _(u'Report')
            },
            {
                'url': '/'.join((info['project_url'], DOCUMENTS_ID)),
                'title': _(u"Documentation")

            },
            {
                'url': '/'.join((info['project_url'], TRACKER_ID)),
                'title': _(u"Tracker")
            }
        ]

        if info['is_project']:
            buttons.insert(0, {
                'url': info['project_url'],
                'title': _(u'Go to Project')
            })

        return buttons

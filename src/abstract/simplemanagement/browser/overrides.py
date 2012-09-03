from plone.app.layout.viewlets.common import PathBarViewlet
from ..interfaces import IProject
from .. import messageFactory as _


class BacklogPathBarViewlet(PathBarViewlet):

    def update(self):
        super(BacklogPathBarViewlet, self).update()
        project = self.breadcrumbs[-1] # pylint: disable=E0203
        self.breadcrumbs = self.breadcrumbs + (
            { 'absolute_url': project['absolute_url'].rstrip('/') + \
                  '/@@backlog',
              'Title': _(u"Backlog") },
        )


class BacklogStoryPathBarViewlet(PathBarViewlet):

    def update(self):
        super(BacklogStoryPathBarViewlet, self).update()
        if IProject.providedBy(self.context.__parent__):
            # pylint: disable=E0203
            project = self.breadcrumbs[-2]
            story = self.breadcrumbs[-1]
            backlog = {
                 'absolute_url': project['absolute_url'].rstrip('/') + \
                     '/@@backlog',
                 'Title': _(u"Backlog")
            }
            self.breadcrumbs = self.breadcrumbs[:-1] + (
                backlog,
                story
            )

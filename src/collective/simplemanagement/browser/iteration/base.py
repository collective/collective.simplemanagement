from Acquisition import aq_inner
from zope.security import checkPermission

from z3c.form.interfaces import IFormLayer

from plone.z3cform import z2
from plone.memoize.instance import memoize

from Products.Five.browser import BrowserView

from ..story.form import AddStoryQuickForm
from ...interfaces import IStoriesListing


class IterationViewMixin(object):

    totals = None

    @memoize
    def stories(self):
        return self.context.stories()

    @memoize
    def totals(self):
        return self.context.totals()

    @property
    def user_can_manage_project(self):
        return checkPermission(
            'simplemanagement.ManageProject', self.context
        )

    def user_can_edit(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    def user_can_add_story(self):
        return checkPermission('simplemanagement.AddStory', self.context)

    def add_story_form(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = AddStoryQuickForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()

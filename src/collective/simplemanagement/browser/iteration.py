from Acquisition import aq_inner
from zope.security import checkPermission

from z3c.form.interfaces import IFormLayer

from plone.z3cform import z2
from plone.memoize.instance import memoize

from Products.Five.browser import BrowserView

from ..story import StoryQuickForm
from ..interfaces import IStoriesListing
from ..interfaces import IIteration


class IterationViewMixin(object):

    totals = None

    @memoize
    def stories(self):
        adpt = IStoriesListing(self.context)
        stories = adpt.stories()
        self.totals = adpt.totals
        return stories

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
        addform = StoryQuickForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()


class View(BrowserView, IterationViewMixin):

    def get_dates(self):
        start = self.context.toLocalizedTime(self.context.start.isoformat())
        end = self.context.toLocalizedTime(self.context.end.isoformat())
        return dict(start=start, end=end)

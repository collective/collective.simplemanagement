from datetime import date
from Acquisition import aq_inner
from zope.security import checkPermission
from z3c.form.interfaces import IFormLayer
from plone.z3cform import z2
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from ...story import ProjectStoryQuickForm
from ...utils import AttrDict


class View(BrowserView):

    @property
    @memoize
    def tools(self):
        return AttrDict({
            'portal_catalog': getToolByName(self.context, 'portal_catalog')
        })

    @property
    def user_can_manage_project(self):
        return checkPermission(
            'simplemanagement.ManageProject', self.context
        )

    def user_can_add_story(self):
        return checkPermission('simplemanagement.AddStory', self.context)

    def add_story_form(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = ProjectStoryQuickForm(
            aq_inner(self.context),
            self.request
        )
        iterations = self.iterations()
        if iterations and iterations['current']:
            addform.container = iterations['current'][0]
        addform.update()
        return addform.render()

    def iterations(self):
        iterations = {
            'past': [],
            'current': [],
            'future': []
        }
        pc = self.tools['portal_catalog']
        raw_iterations = pc.searchResults({
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': 'Iteration',
            'sort_on': 'start',
            'sort_order': 'ascending'
        })
        now = date.today()
        have_iterations = False
        for iteration_brain in raw_iterations:
            iteration = iteration_brain.getObject()
            if iteration.end < now:
                iterations['past'].append(iteration)
                have_iterations = True
            elif iteration.end >= now and iteration.start <= now:
                iterations['current'].append(iteration)
                have_iterations = True
            else:
                iterations['future'].append(iteration)
                have_iterations = True
        if not have_iterations:
            return None
        return iterations

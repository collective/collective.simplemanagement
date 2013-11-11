from datetime import date
from Acquisition import aq_inner
from zope.security import checkPermission
from z3c.form.interfaces import IFormLayer
from plone.z3cform import z2
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

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

    def iterations(self):
        # XXX: do we need this? - alliterations view
        return {}

from zope.component import getMultiAdapter

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from ..utils import get_story
from ..utils import get_project
from ..utils import AttrDict


class BookingView(BrowserView):

    @property
    @memoize
    def tools(self):
        return AttrDict({
            'portal_catalog': getToolByName(self.context, 'portal_catalog')
        })

    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state'
        )

    @property
    def user(self):
        user = None
        portal_state = self.portal_state()
        if not portal_state.anonymous():
            user = portal_state.member()
        return user

    def results(self):
        query = {
            'portal_type': 'Booking',
            'Creator ': self.user.getId(),
            'sort_on': 'booking_date',
            'sort_order': 'descending'
        }

        pc = self.tools['portal_catalog']
        for brain in pc.searchResults(query):
            booking = brain.getObject()
            story = get_story(booking)
            project = get_project(booking)

            yield {
                'title': brain.Title,
                'url': brain.getURL(),
                'date': booking.date,
                'time': booking.time,
                'project': {
                    'title': project.Title(),
                    'url': project.absolute_url()
                },
                'story': {
                    'title': story.Title(),
                    'url': story.absolute_url()
                }
            }

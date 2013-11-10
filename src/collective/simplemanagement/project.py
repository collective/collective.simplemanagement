from zope.interface import implementer
from plone.dexterity.content import Container
from .interfaces import IProject
from .interfaces import IStoriesListing


@implementer(IProject)
class Project(Container):

    def _stories_listing(self):
        return IStoriesListing(self)()

    def stories(self):
        return self._stories_listing().stories

    def totals(self):
        return self._stories_listing().totals

    def get_notes(self):
        notes = self.notes
        if notes:
            return self.notes.output

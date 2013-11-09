from zope.interface import implementer
from plone.dexterity.content import Container
from .interfaces import IProject


@implementer(IProject)
class Project(Container):

    def get_notes(self):
        notes = self.notes
        if notes:
            return self.notes.output

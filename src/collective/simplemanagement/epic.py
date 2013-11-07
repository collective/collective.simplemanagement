from zope.interface import implementer
from plone.dexterity.content import Container

from .interfaces import IEpic


@implementer(IEpic)
class Epic(Container):

    def get_text(self):
        text = self.text
        if text:
            return self.text.output

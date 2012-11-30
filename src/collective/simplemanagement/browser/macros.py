from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView


class Macros(BrowserView):
    template = ViewPageTemplateFile('templates/macros.pt')

    def __getitem__(self, key):
        return self.template.macros[key]

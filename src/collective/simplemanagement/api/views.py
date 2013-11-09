from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse, NotFound
from Products.Five import BrowserView


class Traversable(BrowserView):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(Traversable, self).__init__(context, request)
        self.method = None

    def publishTraverse(self, request, name):
        if self.method is None:
            method = getattr(self, 'do_'+name, None)
            if method is not None and callable(method):
                self.method = 'do_'+name
            return self
        raise NotFound(self, name, request)

    def __call__(self):
        if self.method is None:
            try:
                result = super(Traversable, self).__call__()
            except AttributeError:
                result = self.template()
        else:
            result = getattr(self, self.method)()
        self.method = None
        return result

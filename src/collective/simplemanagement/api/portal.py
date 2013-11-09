from collections import defaultdict
from Products.CMFCore.utils import getToolByName


class LazyTools(defaultdict):

    def __init__(self, context, *args, **kwargs):
        self.context = context
        super(LazyTools, self).__init__(*args, **kwargs)

    def __missing__(self, key):
        return getToolByName(self.context, key)

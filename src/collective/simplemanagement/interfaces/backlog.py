from zope.interface import Interface


class IBacklogView(Interface):
    """A marker interface for the backlog view, that has a custom
    breadcrumb
    """

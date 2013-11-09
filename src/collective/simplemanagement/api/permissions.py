import plone.api
from AccessControl import Unauthorized


def accesscontrol(permission=None):
    def decorator(meth):
        def wrapper(self, *args, **kwargs):
            mt = plone.api.portal.get_tool(name='portal_membership')
            if not mt.checkPermission(permission, self.context):
                raise Unauthorized
            return meth(self, *args, **kwargs)
        return wrapper
    return decorator


def accessreview(permission=None):
    def decorator(meth):
        def wrapper(self, *args, **kwargs):
            """An user can review a story if at least one WF transition
            is available
            """
            wft = plone.api.portal.get_tool(name='portal_workflow')
            wf = wft.getWorkflowsFor(self.context)
            if wf:
                wf = wf[0]
            actions = wf.listActionInfos(object=self.context, max=1)
            if len(actions) == 0:
                raise Unauthorized
            return meth(self, *args, **kwargs)
        return wrapper
    return decorator

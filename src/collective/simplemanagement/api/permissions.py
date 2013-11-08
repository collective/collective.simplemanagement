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

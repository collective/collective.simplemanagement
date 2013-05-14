from Products.CMFCore.utils import getToolByName

from Products.CMFCore.Expression import getExprContext

from Products.Five.browser import BrowserView

from plone.memoize.view import memoize_contextless

from ..utils import timeago


class Helpers(BrowserView):

    def timeago(self, timestamp):
        return timeago(timestamp)

    @memoize_contextless
    def _actions(self):
        pa = getToolByName(self.context, 'portal_actions')
        return pa.listActionInfos(
            categories=['simplemanagement_actions']
        )

    def has_sm_actions(self):
        return bool(self._actions)

    def sm_actions(self, project=None):
        getExprContext(self.context)
        ps = self.context.restrictedTraverse('@@plone_portal_state')
        base_url = ps.portal_url()
        if project is not None:
            base_url = project.absolute_url()
        for i in self._actions():
            current = self.request['URL'].split('/')[-1]
            yield {
                'title': i['title'],
                'id': i['id'],
                'url': '/'.join((
                    base_url,
                    i['url']
                )),
                'description': i['description'],
                'class': ' '.join((
                    i['id'],
                    current == i['id'] and 'selected' or ''
                ))
            }

    @memoize_contextless
    def sm_top_actions(self):
        available = ['dashboard', ]
        return [x for x in self.sm_actions()
                if x['id'] in available]

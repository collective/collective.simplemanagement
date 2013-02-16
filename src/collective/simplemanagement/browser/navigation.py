from zope.interface import implements
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.portlets.portlets.navigation import NavtreeStrategy


class ProjectNavtreeStrategy(NavtreeStrategy):

    implements(INavtreeStrategy)

    hidden_types = ('Story', 'Epic')

    def nodeFilter(self, node):
        result = super(ProjectNavtreeStrategy, self).nodeFilter(node)
        item = node['item']
        if result:
            if item.portal_type in self.hidden_types:
                result = False
            elif item.portal_type == 'Iteration' and \
                    item.review_state != 'active':
                result = False
        return result


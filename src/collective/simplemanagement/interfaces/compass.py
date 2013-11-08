from zope.interface import Interface
from zope.schema import Int
from zope.schema import TextLine
from .. import _


class ICompassSettings(Interface):

    default_plan_length = Int(
        title=_(u"Usual plan length"),
        description=_(u"The number of weeks that the compass plan "
                      u"will span (barring exceptions)"),
        default=2
    )

    minimum_plan_length = Int(
        title=_(u"Minimum plan length"),
        description=_(u"The minimum number of weeks that the compass plan "
                      u"can span"),
        default=1
    )

    maximum_plan_length = Int(
        title=_(u"Maximum plan length"),
        description=_(u"The maximum number of weeks that the compass plan "
                      u"can span"),
        default=4
    )

    projects_folder = TextLine(
        title=_(u"Folder where projects will be creted"),
        description=_(u"The compass will create projects in the specified path"),
        default=u"/projects"
    )

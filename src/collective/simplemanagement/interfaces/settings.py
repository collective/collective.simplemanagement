from decimal import Decimal

from zope import schema
from zope.interface import Interface

from .. import _


class ISettings(Interface):
    """The settings of simplemanagement.
    """

    warning_delta_percent = schema.Decimal(
        title=_(u"Warning delta"),
        description=_(u"The percentage (between 0 and 1) "
                      u"after which a deviation needs to be highlighted"),
        min=Decimal("0.1"),
        max=Decimal("1.0")
    )
    man_day_hours = schema.Decimal(
        title=_(u"Man day hours"),
        description=_(u"The number of hours a person works in a day")
    )
    booking_check_delta_days_start = schema.Int(
        title=_(u"Booking check days delta start")
    )
    booking_check_delta_days_end = schema.Int(
        title=_(u"Booking check days delta end")
    )
    statuses = schema.List(
        title=_(u"Project statuses"),
        value_type=schema.TextLine()
    )
    env_types = schema.List(
        title=_(u"Environment types"),
        value_type=schema.TextLine()
    )
    resource_roles = schema.List(
        title=_(u"Resource roles"),
        value_type=schema.TextLine()
    )
    off_duty_reasons = schema.List(
        title=_(u"Possible reasons to be off duty"),
        value_type=schema.TextLine()
    )
    employees_group = schema.TextLine(
        title=_(u"Employess group"),
        description=_(u"Identifier of the group containing all employees")
    )
    monthly_weeks_before = schema.Int(
        title=_(u"Number of weeks before month"),
        description=_(u"The number of weeks to show in monthly views "
                      u"that actually fall in the previous month")
    )
    monthly_weeks_after = schema.Int(
        title=_(u"Number of weeks after month"),
        description=_(u"The number of weeks to show in monthly views "
                      u"that actually fall in the next month")
    )

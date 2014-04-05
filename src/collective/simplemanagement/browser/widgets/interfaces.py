from zope import schema

from z3c.form.interfaces import IWidget

from ... import _


class IBookingDateWidget(IWidget):
    """Marker interface for the booking form date widget
    """

    def pattern():
        """Returns the date format pattern
        """

    def formatted_value():
        """Returns the formatted value
        """


class ITimeWidget(IWidget):
    """ a time widget
    """

    show_min = schema.Bool(
        title=_(u"Show minutes"),
        default=True
    )

    hour_free_input = schema.Bool(
        title=_(u"Hour free input"),
        default=False
    )

    hour_start = schema.Int(
        title=_(u"Hour start"),
        default=1
    )

    hour_stop = schema.Int(
        title=_(u"Hour stop"),
        default=8
    )


class IBookWidget(IWidget):
    """Booking widget
    """

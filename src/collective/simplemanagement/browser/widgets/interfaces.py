from z3c.form.interfaces import IWidget


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

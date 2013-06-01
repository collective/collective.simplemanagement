from datetime import date

from zope.interface import Interface
from zope import schema

from z3c.relationfield.schema import RelationChoice

from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder

from ..browser.widgets.time_widget import TimeFieldWidget

from .. import _


class IBooking(form.Schema):

    date = schema.Date(
        title=_(u"Date"),
        default=date.today()
    )

    form.widget('time', TimeFieldWidget)
    time = schema.Decimal(title=_(u"Hours"))

    related = RelationChoice(
        title=_(u"Related activity"),
        source=ObjPathSourceBinder(),
        required=False
    )


class IBookingHole(Interface):
    """Explains why someone seemingly hasn't worked on anything for many hours.

    Since bookings keep track of worked time on projects,
    there can be hours of unbooked time for various reasons.

    This object helps keep track of this *missing time*
    so that it is not reported as *unknown hole*.
    """

    day = schema.Date()
    hours = schema.Decimal()
    user_id = schema.TextLine()
    reason = schema.Choice(
        title=_(u"Reason"),
        source="collective.simplemanagement.off_duty_reasons"
    )


class IBookingHoles(Interface):
    """The list of booking holes.

    See :class:`IBookingHole` for details.
    """

    def add(hole):
        """Adds a hole.

        ``hole`` must provide :class:`IBookingHole`
        """

    def remove(user_id, day=None):
        """Removes the hole registered by ``user_id`` for the given ``day``.

        If ``day`` is ``None`` removes everything.
        """

    def __contains__(user_id):
        """Returns true if ``user_id`` is contained.
        """

    def __iter__():
        """Iterates over all the contained holes, in random order
        """

    def iter_user(user_id, from_, to):
        """Return an iterator over the holes inserted for ``user_id``,
        between ``from_`` and ``to``.

        ``from_`` and ``to`` shall be :class:`~datetime.date` objects.
        """

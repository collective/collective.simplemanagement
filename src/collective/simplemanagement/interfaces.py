from decimal import Decimal
from datetime import date

from zope import schema
from zope.interface import Interface
from zope.location.interfaces import ILocation

from z3c.relationfield.schema import RelationChoice

from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.theme.interfaces import IDefaultPloneLayer
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from collective.z3cform.widgets.enhancedtextlines import (
    EnhancedTextLinesFieldWidget,
)
from abstract.z3cform.usertokeninput.widget import UserTokenInputFieldWidget

from . import messageFactory as _


class IQuickForm(Interface):
    title = schema.TextLine(
        title=_(u'Title'),
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )


class IBrowserLayer(IDefaultPloneLayer):
    """The browser layer of the package"""


class IResource(Interface):

    role = schema.Choice(
        title=_(u"Role"),
        source="collective.simplemanagement.roles"
    )
    user_id = schema.TextLine(title=_(u"User ID"))
    active = schema.Bool(title=_(u"Active"),
                         default=True)


class IEnvironment(Interface):

    name = schema.TextLine(title=_(u"Name"))
    env_type = schema.Choice(
        title=_(u"Type"),
        source="collective.simplemanagement.envtypes"
    )
    url = schema.URI(title=_(u"URL"))


class IMilestone(Interface):

    name = schema.TextLine(title=_(u"Name"))
    status = schema.Choice(
        title=_(u"Status"),
        source="collective.simplemanagement.status"
    )
    deadline = schema.Date(title=_(u"Deadline"),
                           required=False)


class IProject(form.Schema):

    customer = schema.TextLine(
        title=_(u"Customer")
    )
    budget = schema.Decimal(
        title=_(u"Budget (man days)"),
        description=_(u"The man days that this project is paid for")
    )
    initial_estimate = schema.Decimal(
        title=_(u"Estimate (man days)"),
        description=_(
            u"The man days required for completion, "
            u"as initially estimated by the project manager"
        ),
        required=False,
        default=Decimal('0.00')
    )
    prj_start_date = schema.Date(
        title=_(u"Start date"),
        default=date.today()
    )
    prj_expected_end_date = schema.Date(
        title=_(u"Expected end date"),
        required=False
    )
    prj_end_date = schema.Date(
        title=_(u"End date"),
        required=False
    )
    classifiers = schema.List(
        title=_(u"Project classifiers"),
        description=_(u"Some keywords that describe the project "
            u"and used technologies"),
        value_type=schema.TextLine(),
        required=False
    )
    form.widget(classifiers=EnhancedTextLinesFieldWidget)

    repositories = schema.List(
        title=_(u"Repositories"),
        description=_(u"The HTTP URLs of the repositories "
                      u"(e.g. https://github.com/company/my.repository/)"),
        value_type=schema.URI(),
        required=False
    )
    environments = schema.List(
        title=_(u"URLs"),
        description=_(u"The URLs of the various online environments "
                      u"(staging, production)"),
        value_type=schema.Object(title=_(u"Environment"),
                                 schema=IEnvironment),
        required=False
    )
    milestones = schema.List(
        title=_(u"Milestones"),
        description=_(u"Milestones are the different phases of the project. "
                      u"Each milestone should formally define "
                      u"a self-sufficient deliverable, "
                      u"that can then be put into production."),
        value_type=schema.Object(title=_(u"Milestone"),
                                 schema=IMilestone),
        required=False
    )
    operatives = schema.List(
        title=_(u"Operatives"),
        description=_(
            u"The user IDs of those that have operative roles in this project "
            u"(coders, designers, project managers, accounts etc.). "
            u"Customers should not be included in this list."
            u"Adding someone here will add them automatically "
            u"as managers to the default tracker."
        ),
        value_type=schema.Object(title=_(u"Resource"),
                                 schema=IResource),
        required=False
    )
    notes = schema.Text(
        title=_(u"Notes"),
        required=False
    )
    form.widget(notes=WysiwygFieldWidget)

    form.omitted('priority')
    priority = schema.Int(
        title=_(u"Priority"),
        default=100,
        min=0
    )


class IIteration(form.Schema):

    start = schema.Date(title=_(u"Start"))
    end = schema.Date(title=_(u"End"))
    estimate = schema.Decimal(
        title=_(u"Estimate (man days)"),
        required=False,
        default=Decimal('0.00')
    )


class IEpic(form.Schema):

    text = schema.Text(title=_(u"Text"))
    estimate = schema.Decimal(
        title=_(u"Estimate (man days)"),
        default=Decimal('0.00')
    )


class IStory(form.Schema):

    text = schema.Text(
        title=_(u"Text"),
        required=False
    )
    estimate = schema.Decimal(
        title=_(u"Estimate (man hours)"),
        default=Decimal('0.00')
    )

    assigned_to = schema.List(
        title=_(u"Assignees"),
        description=_(u"The user IDs of the people "
                      u"that are responsible to act on this story"),
        value_type=schema.TextLine(),
        required=False
    )
    form.widget(assigned_to=UserTokenInputFieldWidget)
    epic = RelationChoice(
        title=_(u"Epic"),
        description=_(u"The epic the story belongs to"),
        source=ObjPathSourceBinder(object_provides=[IEpic.__identifier__, ]),
        required=False
    )
    milestone = schema.Choice(
        title=_(u"Milestone"),
        required=False,
        source="collective.simplemanagement.milestones"
    )


class IBooking(form.Schema):

    date = schema.Date(title=_(u"Date"))
    time = schema.Decimal(title=_(u"Hours"))
    related = RelationChoice(
        title=_(u"Related activity"),
        source=ObjPathSourceBinder(),
        required=False
    )


class IStoriesListing(Interface):

    def stories(project_info=False):
        """return stories details if project_info is True
        each story contains also information about project and iteration
        """

    def totals():
        """return stories' timing
        """


class IMyStoriesListing(IStoriesListing):
    """This adapter return all stories assigned to myself"""


class IBacklogView(Interface):
    """A marker interface for the backlog view, that has a custom
    breadcrumb
    """


class ITimeline(ILocation):
    """Keeps a list of "snapshots" over time.

    Snapshots are the status of an item at a given time,
    in the form of condensed information about it.

    It can be thought of as a versioned, local catalog of an object.
    """

    def snapshot(context, indexes=None, insert=True):
        """Take a snapshot of the context and add it to the timeline.

        ``context`` is the adapter context, which is passed for convenience
        (as :func:`~zope.annotation.factory.factory`
        sometimes wraps the whole thing in a location proxy,
        making everything extra difficult).

        ``indexes`` can optionally restrict snapshotting just to some of them
        (``None`` means *all*).

        If ``insert`` is ``False`` the snapshot isn't inserted
        into the timeline but just returned.

        Returns the snapshot as a dictionary.
        """

    def slice(from_, to, resolution, indexes=None):
        """Produces the variation of indexes over time,
        from a given point in time (``from_``) to another one (``to``).

        ``resolution`` is a ``timedelta`` object
        that represents the resolution of the returned data serie
        (e.g. if ``resolution = timedelta(days=1)``
        all items in the returned serie will be spaced by one day).

        ``indexes`` can optionally restrict slicing to just to some of them
        (``None`` means *all*).

        Returns an iterator whose elements are 2-tuples,
        the first item being the beginning of the time slice
        and the second item being a dictionary whose keys are the indexes
        (if the index is missing for that period,
        it is not present in the dictionary) and the values the values.
        """


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
        title=_(u"Booking check days delta start"),
        description=_(u"The number of days ...")
    )
    booking_check_delta_days_end = schema.Int(
        title=_(u"Booking check days delta end"),
        description=_(u"The number of days ...")
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

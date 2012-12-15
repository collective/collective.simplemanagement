from decimal import Decimal
from zope import schema
from zope.interface import Interface

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

    customer = schema.TextLine(title=_(u"Customer"))
    budget = schema.Int(
        title=_(u"Budget (man days)"),
        description=_(u"The man days that this project is paid for")
    )
    initial_estimate = schema.Int(
        title=_(u"Estimate (man days)"),
        description=_(
            u"The man days required for completion, "
            u"as initially estimated by the project manager"
        )
    )
    prj_start_date = schema.Date(title=_(u"Start date"))
    prj_expected_end_date = schema.Date(title=_(u"Expected end date"))
    prj_end_date = schema.Date(title=_(u"End date"))
    is_external = schema.Bool(
        title=_(u'Is external?'),
        description=_(
            u'Check this field if this project is visible to customer.'),
        required=True,
        default=True,
    )
    classifiers = schema.List(
        title=_(u"Project classifiers"),
        description=_(u"Some keywords that describe the project "
            u"and used technologies"),
        value_type=schema.TextLine()
    )
    form.widget(classifiers=EnhancedTextLinesFieldWidget)

    repositories = schema.List(
        title=_(u"Repositories"),
        description=_(u"The HTTP URLs of the repositories "
                      u"(e.g. https://github.com/company/my.repository/)"),
        value_type=schema.URI()
    )
    environments = schema.List(
        title=_(u"URLs"),
        description=_(u"The URLs of the various online environments "
                      u"(staging, production)"),
        value_type=schema.Object(title=_(u"Environment"),
                                 schema=IEnvironment)
    )
    milestones = schema.List(
        title=_(u"Milestones"),
        description=_(u"Milestones are the different phases of the project. "
                      u"Each milestone should formally define "
                      u"a self-sufficient deliverable, "
                      u"that can then be put into production."),
        value_type=schema.Object(title=_(u"Milestone"),
                                 schema=IMilestone)
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
                                 schema=IResource)
    )
    notes = schema.Text(
        title=_(u"Notes"),
        required=False
    )
    form.widget(notes=WysiwygFieldWidget)


class IIteration(form.Schema):

    start = schema.Date(title=_(u"Start"))
    end = schema.Date(title=_(u"End"))
    estimate = schema.Decimal(title=_(u"Estimate (man days)"))


class IEpic(form.Schema):

    text = schema.Text(title=_(u"Text"))
    estimate = schema.Decimal(title=_(u"Estimate (man days)"))


class IStory(form.Schema):

    text = schema.Text(title=_(u"Text"))
    estimate = schema.Decimal(title=_(u"Estimate (man hours)"))

    assigned_to = schema.List(
        title=_(u"Assignees"),
        description=_(u"The user IDs of the people "
                      u"that are responsible to act on this story"),
        value_type=schema.TextLine()
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

    def stories():
        """return stories details
        """

    def totals():
        """return stories' timing
        """


class IBacklogView(Interface):
    """A marker interface for the backlog view, that has a custom
    breadcrumb
    """


class ITimeline(Interface):
    """Keeps a list of "snapshots" over time.

    Snapshots are the status of an item at a given time,
    in the form of condensed information about it.

    It can be thought of as a versioned, local catalog of an object.
    """

    def snapshot(indexes=None, insert=True):
        """Take a snapshot of the context and add it to the timeline.

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

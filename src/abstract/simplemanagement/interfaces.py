from zope import schema
from zope.interface import Interface

from z3c.relationfield.schema import RelationChoice

from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder

from collective.z3cform.widgets.enhancedtextlines import EnhancedTextLinesFieldWidget
from abstract.z3cform.usertokeninput.widget import UserTokenInputFieldWidget

from . import messageFactory as _


class IResource(Interface):

    role = schema.Choice(
        title=_(u"Role"),
        source="abstract.simplemanagement.roles"
    )
    user_id = schema.TextLine(title=_(u"User ID"))


class IEnvironment(Interface):

    name = schema.TextLine(title=_(u"Name"))
    env_type = schema.Choice(
        title=_(u"Type"),
        source="abstract.simplemanagement.envtypes"
    )
    url = schema.URI(title=_(u"URL"))


class IMilestone(Interface):

    name = schema.TextLine(title=_(u"Name"))
    status = schema.Choice(
        title=_(u"Status"),
        source="abstract.simplemanagement.status"
    )


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


class IIteration(form.Schema):

    start = schema.Date(title=_(u"Start"))
    end = schema.Date(title=_(u"End"))


class IEpic(form.Schema):

    text = schema.Text(title=_(u"Text"))
    estimate = schema.Int(title=_(u"Estimate (man days)"))


class IStory(form.Schema):

    text = schema.Text(title=_(u"Text"))
    estimate = schema.Int(title=_(u"Estimate (man hours)"))

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


class IBooking(form.Schema):

    date = schema.Date(title=_(u"Date"))
    time = schema.Int(title=_(u"Hours"))
    related = RelationChoice(
        title=_(u"Related activity"),
        source=ObjPathSourceBinder(),
        required=False
    )

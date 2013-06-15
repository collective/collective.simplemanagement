from decimal import Decimal
from datetime import date

from zope import schema
from zope.interface import Interface

from plone.directives import form
from plone.app.textfield import RichText

from collective.z3cform.widgets.enhancedtextlines import (
    EnhancedTextLinesFieldWidget,
)

from .. import _


class IResource(Interface):

    role = schema.Choice(
        title=_(u"Role"),
        source="collective.simplemanagement.roles"
    )
    user_id = schema.TextLine(title=_(u"User ID"))
    active = schema.Bool(
        title=_(u"Active"),
        default=True
    )


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
    deadline = schema.Date(
        title=_(u"Deadline"),
        required=False
    )


class IProject(form.Schema):

    customer = schema.TextLine(
        title=_(u"Customer")
    )
    order_number = schema.TextLine(
        title=_(u"Order number"),
        required=False
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
        description=_(
            u"Some keywords that describe the project "
            u"and used technologies"
        ),
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

    notes = RichText(
        title=_(u"Notes"),
        required=False
    )

    form.omitted('priority', 'active')
    priority = schema.Int(
        title=_(u"Priority"),
        default=100,
        min=0
    )
    active = schema.Bool(
        title=_(u"Active"),
        default=True
    )


class IProjectNavigation(Interface):
    """The project navigation portlet
    """

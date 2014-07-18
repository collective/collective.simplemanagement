from decimal import Decimal
from datetime import date

from zope import schema
from zope.interface import Interface
from zope.component import provideAdapter

from z3c.form import widget

from plone.supermodel import model
from plone.autoform import directives as form
from plone.app.textfield import RichText

from collective.select2.field import Select2MultiField
from collective.select2.field import Select2Field

from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow

from .. import _


class ICustomerContact(Interface):
    name = schema.TextLine(title=u"Name")
    role = schema.TextLine(title=u"Role")
    email = schema.TextLine(title=u"Email")
    telephone = schema.TextLine(title=u"Telephone")


class IResource(Interface):

    role = schema.Choice(
        title=_(u"Role"),
        source="collective.simplemanagement.roles"
    )

    user_id = Select2Field(
        title=_(u"User ID"),
        source="collective.simplemanagement.resources",
        search_view=lambda x: '{}/select2-users-search'.format(x),
        required=True
    )

    active = schema.Bool(
        title=_(u"Active"),
        default=True
    )
    compass_effort = schema.Decimal(
        title=_(u"Effort (in man days)"),
        default=Decimal('0.00')
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


class IProject(model.Schema):

    customer = schema.TextLine(
        title=_(u"Customer")
    )

    form.widget(customer_contact=DataGridFieldFactory)
    customer_contact = schema.List(
        title=_(u"Customer contact"),
        value_type=DictRow(
            title=u"Contact",
            schema=ICustomerContact
        )
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
    )
    prj_expected_end_date = schema.Date(
        title=_(u"Expected end date"),
        required=False
    )
    prj_end_date = schema.Date(
        title=_(u"End date"),
        required=False
    )
    classifiers = Select2MultiField(
        title=_(u"Project classifiers"),
        description=_(
            u"Some keywords that describe the project "
            u"and used technologies"
        ),
        value_type=schema.TextLine(),
        search_view=lambda x: '{}/select2-classifier-search'.format(x),
        required=False
    )

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

    notes = RichText(
        title=_(u"Notes"),
        required=False
    )

    form.omitted(
        'priority',
        'active',
        'compass_effort',
        'compass_notes',
        'operatives'
    )
    priority = schema.Int(
        title=_(u"Priority"),
        default=100,
        min=0
    )
    active = schema.Bool(
        title=_(u"Active"),
        default=True
    )
    compass_effort = schema.Decimal(
        title=_(u"Effort (in man days)"),
        default=Decimal('0.00')
    )
    compass_notes = schema.Text(
        title=_(u"Notes"),
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


def default_date(data):
    return date.today()

provideAdapter(
    widget.ComputedWidgetAttribute(
        default_date,
        field=IProject['prj_start_date']
    ),
    name='default'
)


class IProjectNavigation(Interface):
    """The project navigation portlet
    """

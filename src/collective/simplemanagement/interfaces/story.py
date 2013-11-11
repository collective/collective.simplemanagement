from decimal import Decimal

from zope import schema
from zope.interface import Interface

from z3c.relationfield.schema import RelationChoice

from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.textfield import RichText

# from abstract.z3cform.usertokeninput.widget import UserTokenInputFieldWidget

from ..browser.widgets.time_widget import TimeFieldWidget
from .. import _


class IIteration(form.Schema):

    start = schema.Date(title=_(u"Start"))
    end = schema.Date(title=_(u"End"))
    estimate = schema.Decimal(
        title=_(u"Estimate (man days)"),
        required=False,
        default=Decimal('0.00')
    )


class IEpic(form.Schema):

    text = RichText(title=_(u"Text"))
    estimate = schema.Decimal(
        title=_(u"Estimate (man days)"),
        default=Decimal('0.00')
    )


class IStory(form.Schema):

    text = schema.Text(
        title=_(u"Text"),
        required=False
    )

    form.widget('estimate',
                TimeFieldWidget,
                show_min=False,
                hour_free_input=True)
    estimate = schema.Decimal(
        title=_(u"Estimate (man hours)"),
        default=Decimal('0.00')
    )

    assigned_to = schema.List(
        title=_(u"Assignees"),
        description=_(u"The user IDs of the people "
                      u"that are responsible to act on this story"),
        # value_type=schema.TextLine(),
        value_type=schema.Choice(
            title=_(u"User ID"),
            source="collective.simplemanagement.resources"
        ),
        required=False
    )
    # form.widget(assigned_to=UserTokenInputFieldWidget)

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


class IStoriesListing(Interface):

    def stories(project_states=None, story_states=None, project_info=False):
        """return stories details if project_info is True
        each story contains also information about project and iteration.

        Stories can be filtered also by project review state and
        story review state.
        """

    def totals():
        """return stories' timing
        """


class IUserStoriesListing(IStoriesListing):
    """This adapter return all stories assigned to a specific user
    """

    def stories(project_states=None, story_states=None,project_info=False,
                user_id=None):
        """return stories details if project_info is True
        each story contains also information about project and iteration

        This method returns all stories assigned to the current
        logged in user or filters stories by user_id parameter
        and project review state and story review state
        """

from zope import schema
from plone.directives import form
from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from . import messageFactory as _


class IProject(form.Schema):

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


class IIteration(form.Schema):

    start = schema.Date(title=_(u"Start"))
    end = schema.Date(title=_(u"End"))


class IStory(form.Schema):

    text = schema.Text(title=_(u"Text"))
    estimate = schema.Int(title=_(u"Estimate (man hours)"))
    epic = RelationChoice(
        title=_(u"Epic"),
        description=_(u"The epic the story belongs to"),
        source=ObjPathSourceBinder(object_provides=[IEpic.__identifier__, ]),
        required=False
    )


class IEpic(form.Schema):

    estimate = schema.Int(title=_(u"Estimate (man days)"))


class IBooking(form.Schema):

    date = schema.Date(title=_(u"Date"))
    time = schema.Int(title=_(u"Hours"))
    related = RelationChoice(
        title=_(u"Related activity"),
        source=ObjPathSourceBinder(),
        required=False
    )

# pylint: disable=W0613
from zope.interface import Interface
from zope import schema

from z3c.form import form, field, button
from plone.z3cform.layout import wrap_form

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from abstract.z3cform.usertokeninput.widget import UserTokenInputFieldWidget

from ..interfaces import IStory
from .. import messageFactory as _


class IBaseQuickedit(Interface):
    title = schema.TextLine(
        title=_(u'Title'),
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )


class BaseqQuickeditAdapter(object):
    def __init__(self, context):
        self.context = context

    def get_title(self):
        return self.context.Title()

    def set_title(self, value):
        self.context.title = value

    title = property(get_title, set_title)

    def get_description(self):
        return self.context.Description()

    def set_description(self, value):
        self.context.description = value

    description = property(get_description, set_description)


class BaseQuickeEdit(form.EditForm):
    name = "quickedit_form"

    def redirect(self):
        self.request.response.redirect(
            location=self.context.absolute_url())

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

        ptool = getToolByName(self.context, 'plone_utils')
        ptool.addPortalMessage(self.status)

        self.redirect()

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.redirect()


class StoryQuickeditForm(BaseQuickeEdit):
    fields = field.Fields(IBaseQuickedit) + field.Fields(IStory).select(
        'text',
        'estimate',
        'assigned_to',
        'epic')
    fields['assigned_to'].widgetFactory = UserTokenInputFieldWidget


StoryQuickedit = wrap_form(
    StoryQuickeditForm,
    # index=ViewPageTemplateFile('templates/quickedit_form.pt')
)

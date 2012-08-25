# pylint: disable=W0613
from zope.interface import implements

from z3c.form import form, field, button
from plone.z3cform.layout import wrap_form

from Products.CMFCore.utils import getToolByName
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from abstract.z3cform.usertokeninput.widget import UserTokenInputFieldWidget

from ..interfaces import IStory
from ..interfaces import IQuickForm

from .. import messageFactory as _


class BaseqQuickFormAdapter(object):
    implements(IQuickForm)

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
    noChangesMessage = _(u"No changes were applied.")
    successMessage = _(u'Data successfully updated.')

    def redirect(self):
        self.request.response.redirect(
            location='%s/quickedit?ajax_load=1&ajax_include_head=1' % \
                self.context.absolute_url()
        )

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
        ptool = getToolByName(self.context, 'plone_utils')
        ptool.addPortalMessage(self.noChangesMessage)
        self.redirect()


class StoryQuickeditForm(BaseQuickeEdit):
    fields = field.Fields(IQuickForm) + field.Fields(IStory).select(
        'text',
        'estimate',
        'assigned_to',
        'epic')
    fields['assigned_to'].widgetFactory = UserTokenInputFieldWidget


StoryQuickedit = wrap_form(
    StoryQuickeditForm,
    # index=ViewPageTemplateFile('templates/quickedit_form.pt')
)

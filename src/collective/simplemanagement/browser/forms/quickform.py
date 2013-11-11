# pylint: disable=W0613
from zope.interface import implementer

from z3c.form import form, button
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ...interfaces import IQuickForm
from ... import _


class AddQuickForm(form.Form):
    template = ViewPageTemplateFile("templates/quickform.pt")
    ignoreContext = True

    # a string to represent a knockoutjs actions
    # to use in data-bind="{knockout_action}"
    knockout_action = None
    @button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return


@implementer(IQuickForm)
class BaseQuickFormAdapter(object):

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


class EditQuickForm(form.EditForm):
    template = ViewPageTemplateFile("templates/quickform.pt")
    name = 'edit-quickform'

    noChangesMessage = _(u"No changes were applied.")
    successMessage = _(u'Data successfully updated.')

    def redirect(self):
        self.request.response.redirect(
            location=self.context.absolute_url()
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

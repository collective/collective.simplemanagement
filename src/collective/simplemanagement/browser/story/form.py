from z3c.form import field, form, button

from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.z3cform.layout import wrap_form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ..widgets.time_widget import TimeFieldWidget
from ..forms.quickform import AddQuickForm
from ..forms.quickform import EditQuickForm

from ... import api
from ...interfaces import IStory
from ...interfaces import IQuickForm
from ... import _


class AddStoryQuickForm(AddQuickForm):
    knockout_action = "submit: addStory"

    @property
    def action(self):
        return '{0}/add-story'.format(self.context.absolute_url())

    @property
    def fields(self):
        fields = field.Fields(IQuickForm)
        fields += field.Fields(IStory).select(
            'estimate',
            'text',
            'assigned_to'
        )
        fields += field.Fields(ICategorization).select('subjects')
        fields['estimate'].widgetFactory = TimeFieldWidget
        return fields

    def updateWidgets(self):
        super(AddStoryQuickForm, self).updateWidgets()
        self.widgets['estimate'].hour_free_input = 1
        self.widgets['estimate'].show_min = 0

    def updateActions(self):
        super(AddStoryQuickForm, self).updateActions()
        self.actions['add'].addClass("allowMultiSubmit")


class StoryEditQuickForm(EditQuickForm):
    form.extends(EditQuickForm)

    fields = field.Fields(IQuickForm) + field.Fields(IStory).select(
        'text',
        'estimate',
        'assigned_to'
    )


Quickedit = wrap_form(StoryEditQuickForm)

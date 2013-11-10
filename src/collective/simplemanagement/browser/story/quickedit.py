from z3c.form import field
from plone.z3cform.layout import wrap_form
from abstract.z3cform.usertokeninput.widget import UserTokenInputFieldWidget
from ...interfaces import IStory
from ...interfaces import IQuickForm
from ..quickforms import BaseQuickeEdit


class QuickeditForm(BaseQuickeEdit):
    fields = field.Fields(IQuickForm) + field.Fields(IStory).select(
        'text',
        'estimate',
        'assigned_to',
        'epic')
    fields['assigned_to'].widgetFactory = UserTokenInputFieldWidget


Quickedit = wrap_form(QuickeditForm)

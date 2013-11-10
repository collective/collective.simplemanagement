from ...story import StoryQuickForm
from ..ajaxforms import Mixin
from ... import _


class AddStory(Mixin):

    FormKlass = StoryQuickForm
    creation_form = True
    created_message = _(u'Created story:')

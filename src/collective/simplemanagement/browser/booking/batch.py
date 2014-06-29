from zope.interface import Interface
from zope import schema

from plone.z3cform import layout

from z3c.form import form
from z3c.form import button
from z3c.form import field
from z3c.relationfield.schema import RelationChoice

import plone.api
from plone.formwidget.contenttree import UUIDSourceBinder
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject

from Products.Five import BrowserView

from ... import _
from ...interfaces import IStory
from ...interfaces import IProject
from ... import api
from ..widgets.book_widget import REGEXP


COOKIE_NAME = '_sm_booking_batch'


def get_bookings_uids(request):
    result = []
    if COOKIE_NAME in request:
        result = request[COOKIE_NAME].split(':')
        request.response.expireCookie(COOKIE_NAME)
    return result


class Actor(object):

    def __init__(self, uids):
        self.uids = uids
        self.storage = api.booking.get_storage()

    def bookings(self):
        for uid in self.uids:
            booking = self.storage[uid]
            yield booking
            self.storage.reindex(booking)

    def transferTo(self, uuid):
        """Transfers to a project or story
        """
        target = uuidToObject(uuid)
        story = None
        project = None
        if IStory.providedBy(target):
            project = api.content.get_project(target)
            story = target
        elif IProject.providedBy(target):
            project = target
        for booking in self.bookings():
            if project is not None:
                new_references = [
                    r for r in booking.references if \
                        r[0] not in ('Project', 'Story')
                ]
                booking.text = REGEXP.sub(
                    lambda m: '' if m.group(1) == '@' else m.group(0),
                    booking.text
                )
                if story is not None:
                    new_references.insert(0, ('Story', IUUID(story)))
                    booking.text = u'@{story} '.format(
                        story=story.getId()
                    ) + booking.text
                new_references.insert(0, ('Project', IUUID(project)))
                booking.text = u'@{project} '.format(
                    project=project.getId()
                ) + booking.text
                booking.references = new_references

    def replaceTags(self, from_tag, to_tag):
        """Replaces tags
        """
        for booking in self.bookings():
            if from_tag in booking.tags:
                booking.text = REGEXP.sub(
                    lambda m: u'#'+to_tag \
                        if m.group(1) == '#' and m.group(2) == from_tag \
                        else m.group(0),
                    booking.text
                )
                booking.tags = set([
                    t if t != from_tag else to_tag for t in booking.tags
                ])


class BaseForm(form.Form):

    def update(self):
        self.request.set('disable_border', 1)
        super(BaseForm, self).update()

    def nextURL(self):
        return self.context.absolute_url()


class ITransferForm(Interface):

    project_or_story = RelationChoice(
        title=_(u"Project or story"),
        description=_(u"Project or story where to transfer the booking"),
        source=UUIDSourceBinder(portal_type=('Project', 'Story'))
    )


class TransferForm(BaseForm):
    fields = field.Fields(ITransferForm)
    ignoreContext = True

    @button.buttonAndHandler(u'Transfer')
    def handle_transfer(self, __):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        actor = Actor(get_bookings_uids(self.request))
        actor.transferTo(data['project_or_story'])
        plone.api.portal.show_message(
            message=_(u"Bookings transferred"),
            request=self.request,
            type='info'
        )
        self.request.response.redirect(self.nextURL())


TransferView = layout.wrap_form(TransferForm)


class IReplaceForm(Interface):

    from_tag = schema.TextLine(
        title=_(u"From"),
        description=_(u"The tag that has to be replaced")
    )

    to_tag = schema.TextLine(
        title=_(u"To"),
        description=_(u"The tag you are going to replace it with")
    )


class ReplaceForm(BaseForm):
    fields = field.Fields(IReplaceForm)
    ignoreContext = True

    @button.buttonAndHandler(u'Replace')
    def handle_replace(self, __):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        actor = Actor(get_bookings_uids(self.request))
        actor.replaceTags(
            data['from_tag'],
            data['to_tag']
        )
        plone.api.portal.show_message(
            message=_(u"Tags replaced"),
            request=self.request,
            type='info'
        )
        self.request.response.redirect(self.nextURL())


ReplaceView = layout.wrap_form(ReplaceForm)


class BatchIntermediate(BrowserView):

    def __call__(self):
        bookings = self.request.form.get('bookings', [])
        url = None
        if 'transfer_to' in self.request.form:
            url = self.context.absolute_url() + '/@@batch-transfer'
        elif 'replace_tags' in self.request.form:
            url = self.context.absolute_url() + '/@@batch-replace'
        if url is None:
            url = self.context.absolute_url()
            plone.api.portal.show_message(
                message=_(u"No action was selected!"),
                request=self.request,
                type='error'
            )
        if len(bookings) > 0:
            self.request.response.setCookie(COOKIE_NAME, ':'.join(bookings))
        else:
            url = self.context.absolute_url()
            plone.api.portal.show_message(
                message=_(u"No bookings were selected!"),
                request=self.request,
                type='error'
            )
        self.request.response.redirect(url)
        return u''

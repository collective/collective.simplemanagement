#-*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from ... import logger
from ... import api


class AjaxFormAction(BrowserView):
    """Mixin klass for ajax form action views.

    This browserview can be used to manage an ajax form
    submit and response.

    How to Extend this form:

    class MyForm(form.Form):
        ...
        @property
        def action(self):
            return 'url/of-my-form-action-view'

    class MyFormAction(AjaxFormAction):
        form_class = MyForm

        def form_action(self, data):
            "do something with data"
            return "something serializable in json"
    """

    form_class = None

    @property
    def error_msg(self):
        return "An error occurred while processing '%s' view" % self.__name__

    def form_action(self, data):
        raise NotImplementedError

    def process(self):
        form = self.form_class(self.context, self.request)
        form.update()
        data, errors = form.extractData()
        if errors:
            messages = []
            for er in errors:
                messages.append(
                    '{0}: {1}'.format(
                        self.context.translate(er.field.title),
                        self.context.translate(er.message)
                    )
                )
            return {
                "error": True,
                "messages": messages
            }
        return self.form_action(data)

    @api.jsonutils.jsonmethod()
    def __call__(self):
        results = {
            "error": False,
            "messages": ()
        }

        try:
            results = self.process()
        except Exception, e:  # pylint: disable=W0703
            logger.exception(self.error_msg)
            results["error"] = True
            results["messages"] = (self.error_msg, )

        return results

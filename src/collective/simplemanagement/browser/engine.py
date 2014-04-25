#-*- coding: utf-8 -*-

# taken from https://pypi.python.org/pypi/anthill.tal.macrorenderer/
# and updated

from Acquisition import aq_inner
from StringIO import StringIO
from zope.tal.talinterpreter import TALInterpreter


class MacroRenderer(object):
    """ This engine makes it possible to render single macros
        from a page template using pure python code. """

    def __init__(self, pagetemplate, macroname, context=None):
        pagetemplate._cook()
        self.pt = pagetemplate
        self.mn = macroname
        self.context = context

        try:
            self.m_program = self.pt.macros[self.mn]
        except KeyError:
            raise Exception('Did not find macro named %s' % self.mn)

    def _raise(self):
        raise Exception(
            'It seems that there is no context provided for the template.'
            'I can fix that but you need to provide me with a context arg.'
        )

    def _ensure_context(self):
        """ Can happen that there is not enough context provided """

        if not hasattr(self.pt, 'context') and self.context is None:
            self._raise()

        # fix context as sometimes there is no context available
        if self.context is not None:
            _act = aq_inner(self.context)
            # self.pt = self.pt.__of__(_act)
            self.pt.context = _act

    def __call__(self, **kw):
        """ Returns rendered macro data. You can pass options. """

        self._ensure_context()

        output = StringIO('')
        try:
            context = self.pt.pt_getContext()
        except TypeError:
            self._raise()

        # context['options'] = kw
        context.update(kw)

        TALInterpreter(
            self.m_program,
            None,
            self.pt.pt_getEngineContext(context),
            output)()

        # update buflist to avoid Unicodedecode Error
        buflist = []
        for i in output.buflist:
            if not isinstance(i, unicode):
                i = i.decode('utf-8')
            buflist.append(i)
        output.buflist = buflist

        return output.getvalue()

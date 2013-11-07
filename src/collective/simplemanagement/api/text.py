from Products.CMFCore.utils import getToolByName


def get_text(context, text,
             source_mimetype='text/x-web-markdown',
             target_mimetype=None):
    """ return the body text of an item
    """
    transforms = getToolByName(context, 'portal_transforms')

    if target_mimetype is None:
        target_mimetype = 'text/x-html-safe'

    if text is None:
        return ''

    if isinstance(text, unicode):
        text = text.encode('utf8')
    return transforms.convertTo(target_mimetype,
                                text,
                                context=context,
                                mimetype=source_mimetype).getData()


def shorten(value, length):
    """Shortens a string (generally a title) into a recognizable length-wide
    identifier.

    Example:

        >>> shorten(u'Account', 3)
        u'Acc'
        >>> shorten(u'Project Manager', 3)
        u'PM'
        >>> shorten(u'Developer', 3)
        u'Dev'
        >>> shorten(u'Designer', 3)
        u'Des'
        >>> shorten(u'Sysadmin', 3)
        u'Sys'

    """
    value = value.split(u' ')
    if len(value) == 1:
        return value[0][:length]
    else:
        return u''.join(c[0].upper() for c in value[:length])

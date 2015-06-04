from .configure import DECIMAL_QUANT


def encode(value, doseq=True, to_encoding='utf-8'):
    if isinstance(value, (list, tuple)) and doseq:
        return [encode(i) for i in value]
    if isinstance(value, unicode):
        return value.encode(to_encoding)
    return value


def quantize(value):
    return value.quantize(DECIMAL_QUANT)


def boolize(value):
    if value.lower() in ('1', 'on', 'true'):
        return True
    return False


class AttrDict(dict):
    """ a smarter dict
    """

    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        self[k] = v


class LazyList(list):
    """Lazy list with custom formatting for items.
    Initialize it w/ a set of items and a method
    that will be used to format returned items.
    """

    def __init__(self, items, format_method):
        super(LazyList, self).__init__(items)
        self.format_method = format_method

    def __getslice__(self, start, stop):
        """ deprecated but used in python2.7
        """
        elements = super(LazyList, self).__getslice__(start, stop)
        for i in elements:
            yield self.format_item(i)

    def __getitem__(self, index):
        elements = super(LazyList, self).__getitem__(index)
        return self.format_item(elements)

    def __iter__(self):
        elements = super(LazyList, self).__iter__()
        for i in elements:
            yield self.format_item(i)

    def format_item(self, item):
        return self.format_method(item)

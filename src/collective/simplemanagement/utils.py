from .configure import DECIMAL_QUANT


def encode(value, to_encoding='utf-8'):
    if isinstance(value, unicode):
        return value.encode('utf-8')
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

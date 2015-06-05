# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import getaddresses
from email.utils import formataddr


class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


EMAIL_HEADERS = {'From', 'To', 'Cc', 'Bcc'}
NORM_EXCLUDED_HEADERS = {
    'Date', 'References', 'Message-ID',
    'X-Riferimento-Message-ID',
    'X-Trasporto'
}


def encode_body(body):
    """Encode the body in the clearer endcoding that supports, anyway take
    care of non-ascii characters.
    """
    for body_charset in ('us-ascii', 'iso-8859-1', 'utf-8'):
        try:
            body.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break
    return body_charset, body.encode(body_charset)


def normalize_headers(mapping):
    """Iterates over the given mapping containing header_name, header and
    normalizes it so that it can be added to the message without known
    problems. This will apply the following logic:

    - for 'email' headers (those in the set From, To, Cc, Bcc): split
      the value by parsing the (name, email) tuples; convert the name
      using Header class, join back 'name <email>' strings, and then
      back to the value;

    - do not do anything on dates or others in NORM_EXCLUDED_HEADERS;

    - for other headers just apply the Header class encoding to the
      value;

    WARNING: this function considers the mapping to contain unicode
    keys and values. It doesn't enforces it but you must know that
    only if fed with unicode instances the Header class does
    the-right-thing (which is to encode only when it's needed), if
    it's fed with strings it will encode the passed in values
    everytime.

    """
    result = {}
    for hname, hvalue in mapping.iteritems():
        if not hvalue:
            continue
        elif hname in EMAIL_HEADERS:
            # split addresses in (name, email) tuples
            addresses = getaddresses([hvalue])
            out_addrs = []
            for name, email in addresses:
                if name:
                    # encode only the name part
                    name = Header(name, 'utf-8').encode()
                else:
                    name = str()
                if isinstance(email, unicode):
                    # make sure email part is valid ascii but don't
                    # encode it, with the risk of loosing data
                    # WARN: maybe encode with 'ignore'
                    email = email.encode('us-ascii')
                # join back (name, email) to 'name <email>' strings
                out_addrs.append(formataddr((name, email)))
            # name and email have to be strings here
            hvalue = str(', ').join(out_addrs)
        elif hname in NORM_EXCLUDED_HEADERS:
            # just do encoding to ascii
            if isinstance(hvalue, unicode):
                hvalue = hvalue.encode('us-ascii')
        else:
            hvalue = Header(hvalue, 'utf-8').encode()
        if isinstance(hname, unicode):
            hname = hname.encode('us-ascii')
        result[hname] = hvalue
    return result


def prepare_email_content(text, mfrom, mto, msubject,
                          html=True, html_text=None):
    if html or text.startswith('<html'):
        # Create message container -
        # the correct MIME type is multipart/alternative.
        outer = MIMEMultipart('alternative')

        # Record the MIME types of both parts - text/plain and text/html.
        charset, encoded_body = encode_body(html_text or text)
        text_part = MIMEText(strip_tags(encoded_body), 'plain', charset)
        html_part = MIMEText(encoded_body, 'html', charset)
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message,
        # in this case the HTML message, is best and preferred.
        outer.attach(text_part)
        outer.attach(html_part)
    else:
        outer = MIMEMultipart()
        outer.attach(MIMEText(text, _charset="utf-8"))

    # prepare headers
    headers = {
        'Subject': msubject,
        'From': mfrom,
        'To': mto,
    }
    for k, v in headers.iteritems():
        # make sure we have all unicode strings
        try:
            headers[k] = v.decode('utf-8')
        except:
            pass
    norm_headers = normalize_headers(headers)
    map(outer.add_header, *zip(*norm_headers.iteritems()))

    # Content-Transfer-Encoding: 8bit
    # Content-Type: text/html; charset="UTF-8"
    outer.add_header('Content-Transfer-Encoding', '8bit')
    outer.add_header('Content-Type', 'text/html; charset="UTF-8"')
    outer.set_charset('utf-8')

    return outer.as_string()

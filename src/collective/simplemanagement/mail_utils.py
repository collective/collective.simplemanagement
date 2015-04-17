# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
try:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.header import Header
except ImportError:
    # this is to support name changes
    # from version 2.4 to version 2.5
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.Header import Header

try:
    from zope.app.component.hooks import getSite
    # plone 3
except ImportError:
    from zope.component.hooks import getSite


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


def prepare_email_content(text, mfrom, mto, msubject, html=True, html_text=None):
    if html or text.startswith('<html'):
        # Create message container - the correct MIME type is multipart/alternative.
        outer = MIMEMultipart('alternative')

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(strip_tags(text), 'plain', _charset="utf-8")
        part2 = MIMEText(html_text or text, 'html', _charset="utf-8")
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        outer.attach(part1)
        outer.attach(part2)
    else:
        outer = MIMEMultipart()
        outer.attach(MIMEText(text, _charset="utf-8"))

    # make sure we send utf8 only
    outer['Subject'] = Header(msubject, 'utf-8')
    outer['From'] = Header(mfrom, 'utf-8')
    outer['To'] = Header(mto, 'utf-8')
    # Content-Transfer-Encoding: 8bit
    # Content-Type: text/html; charset="UTF-8"
    outer.add_header('Content-Transfer-Encoding', '8bit')
    outer.add_header('Content-Type', 'text/html; charset="UTF-8"')
    outer.set_charset('utf-8')

    return outer.as_string()

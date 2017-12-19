# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2017 Taro Sato
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import requests

from .router import Router


class Slack(Router):

    def __init__(self,
                 webhook_url,
                 channel=None,
                 color=None,
                 title=None,
                 text=None,
                 footer=None):
        super().__init__()
        self.webhook_url = webhook_url
        self.channel = channel
        self.color = color or '#eeeeee'
        self.title = title or 'Message from {HOSTNAME}'
        self.text = text or '```{MESSAGE}```'
        self.footer = footer or '{HOSTNAME}:{LOGFILE}:{LINENO}'

    def send(self, payload):
        return requests.post(self.webhook_url, json=payload)

    def send_hello(self):
        import kikori
        text = 'Hello from kikori v{}!'.format(kikori.__version__)
        payload = {'fallback': text,
                   'text': text,
                   'username': 'kikori',
                   'icon_emoji': ':evergreen_tree:'}
        return self.send(payload)

    def payload(self, message, cursor, groupdict, color=None, title=None,
                text=None, footer=None, channel=None):
        format_args = {'HOSTNAME': self.hostname,
                       'LOGFILE': cursor.path,
                       'LINENO': cursor.line,
                       'MESSAGE': message}
        format_args.update(**groupdict)

        color = color or self.color
        title = (title or self.title).format(**format_args)
        text = (text or self.text).format(**format_args)
        footer = (footer or self.footer).format(**format_args)
        channel = channel or self.channel

        payload = {
            'fallback': title + '(' + footer + ')',
            'attachments': [{
                'color': color,
                'title': title,
                'text': text,
                'footer': footer,
                'mrkdwn_in': ['text']}],
            'username': 'kikori',
            'icon_emoji': ':evergreen_tree:'}
        if channel:
            payload['channel'] = channel

        return payload

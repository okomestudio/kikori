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

    def send(self, message, cursor, match, **kwargs):
        format_args = {'HOSTNAME': self.hostname,
                       'LOGFILE': cursor.path,
                       'LINENO': cursor.line,
                       'MESSAGE': message}
        format_args.update(**match.groupdict())

        color = kwargs.get('color', self.color)
        title = kwargs.get('title', self.title).format(**format_args)
        text = kwargs.get('text', self.text).format(**format_args)
        footer = kwargs.get('footer', self.footer).format(**format_args)

        payload = {
            'fallback': title + '(' + footer + ')',
            'attachments': [{
                'color': color,
                'title': title,
                'text': text,  # '```' + message + '```',
                'footer': footer,
                'mrkdwn_in': ['text']}],
            'username': 'kikori',
            'icon_emoji': ':evergreen_tree:'}

        if self.channel:
            payload['channel'] = self.channel

        return requests.post(self.webhook_url, json=payload)

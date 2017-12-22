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
import json
import logging
import re

from .handler import create_message
from .handler import EventHandler


log = logging.getLogger(__name__)


def _load_pattern(pattern):
    if not isinstance(pattern, dict):
        return re.compile(pattern)
    result = {}
    for key, value in pattern.items():
        result[key] = _load_pattern(value)
    return result


class JSONLoggerHandler(EventHandler):

    def _load_trigger(self, trigger):
        trigger['pattern'] = _load_pattern(trigger['pattern'])
        return trigger

    def _build_message(self, cursor, message, line):
        # This must be a complete JSON-parsable line
        if message.text is None:
            # This happens when this is the very first message
            # text line parsed from stream.
            message.text = line
        self._process_message(message)

        # Start buffering the new message
        message = create_message(line, cursor)
        return message

    def _match(self, pattern, obj):
        resultdict = {}
        if isinstance(pattern, dict):
            for key, value in pattern:
                if key not in obj:
                    return None
                resultdict = value.match(obj[key])
        else:
            if pattern == obj:
                resultdict = obj
        return resultdict or None

    def _get_matchable_object(self, text):
        return json.loads(text)

    def _render_object(self, obj):
        return json.dumps(obj)

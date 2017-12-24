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

from .handler import create_message
from .handler import EventHandler


class JSONLoggerHandler(EventHandler):

    def _process_file(self, f):
        path = self._get_full_path(f.name)

        cursor, message = self._cache[path]
        f.seek(cursor.pos)

        while 1:
            # Read a line from the current position, including the
            # newline at the end
            s = f.readline()

            if not s.endswith('\n'):
                # When `s` is not ending with a newline, it means
                # either (1) the cursor is at the end of the file with
                # the last line fully read previously or (2) the last
                # line in the file is partially read and more might
                # stream in on the next flush. Since there is no way
                # to know if the message still follows or the next
                # message starts, keep the cursor in the previous
                # position and re-read when more bytes come in on the
                # next modification.
                self._cache[path] = cursor, message
                break

            cursor.line += 1
            cursor.pos = f.tell()

            # This must be a complete JSON-parsable line

            if message.text is None:
                # This happens when this is the very first message
                # text line parsed from stream.
                message.text = s
            self._process_message(message)

            # Start buffering the new message
            message = create_message(s, cursor)

    def _match_text(self, pattern, text):
        return {'matched': True}

    def _format_text_for_matching(self, text):
        return json.loads(text)

    def _format_text_for_view(self, text):
        return json.dumps(text)

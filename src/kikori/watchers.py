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
import copy
import logging
import os
import re
import threading
from types import SimpleNamespace

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer  # noqa

from .utils import count_lines


log = logging.getLogger(__name__)


def _create_cursor(path, pos, line):
    return SimpleNamespace(path=path, pos=pos, line=line)


def _create_message(text, cursor):
    return SimpleNamespace(text=text, cursor=copy.copy(cursor))


class EventHandler(LoggingEventHandler):

    def __init__(self, filename, text_pattern, triggers, routers, **kwargs):
        super(EventHandler, self).__init__(**kwargs)
        self._cache = {}
        self.filename = re.compile(filename)
        self.text_pattern = re.compile(text_pattern)

        self.triggers = []
        for trigger in triggers:
            trigger['text_pattern'] = re.compile(trigger['text_pattern'])
            self.triggers.append(trigger)

        self.routers = routers

        self._lock = threading.Lock()

    def dispatch(self, event):
        if self._is_valid_event(event):
            return super().dispatch(event)

    def on_created(self, event):
        with self._lock:
            fullpath = self._get_full_path(event.src_path)
            with open(event.src_path) as f:
                self._create_cache_entry(fullpath, f)

    def on_deleted(self, event):
        with self._lock:
            self._remove_from_cache(event.src_path)

    def on_modified(self, event):
        with self._lock:
            with open(event.src_path, 'r') as f:
                self._process_file(f)

    def on_moved(self, event):
        with self._lock:
            self._remove_from_cache(event.src_path)

    def all_watched_files(self, dir):
        for root, dirs, filenames in os.walk(dir):
            for filename in filenames:
                if not self._is_valid_filename(filename):
                    continue
                yield self._get_full_path(os.path.join(root, filename))

    def init(self, dir):
        for fullpath in self.all_watched_files(dir):
            with open(fullpath) as f:
                cache = self._create_cache_entry(fullpath, f)
                # line = count_lines(f)
                # pos = f.tell()
                # cursor = _create_cursor(path=fullpath, pos=pos, line=line)
                # message = _create_message(None, cursor)
                # self._cache[fullpath] = cursor, message
            log.info('Caching current state of watched file %s: %r',
                     fullpath, cache)

    def _create_cache_entry(self, fullpath, f):
        line = count_lines(f)
        pos = f.tell()
        cursor = _create_cursor(path=fullpath, pos=pos, line=line)
        message = _create_message(None, cursor)
        self._cache[fullpath] = cursor, message
        return self._cache[fullpath]

    def _is_valid_filename(self, filename):
        return self.filename.match(filename)

    def _is_valid_event(self, event):
        return (not event.is_directory and
                self._is_valid_filename(event.src_path))

    def _get_full_path(self, path):
        return os.path.abspath(path)

    def _remove_from_cache(self, path):
        path = self._get_full_path(path)
        if path in self._cache:
            del self._cache[path]

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

            if self.text_pattern.match(s):
                # The message starts from this line, so the currently
                # buffered message is complete
                if message.text is None:
                    # This happens when this is the very first message
                    # text line parsed from stream.
                    message.text = s
                self._process_message(message)

                # Start buffering the new message
                message = _create_message(s, cursor)
            else:
                # This is a non-first line in a multiline message and
                # should be bufferred.
                if message.text:
                    message.text += s

    def _process_message(self, message):
        if not message.text:
            return

        text = message.text.rstrip('\n')
        cursor = message.cursor

        for trigger in self.triggers:
            mobj = trigger['text_pattern'].match(text)
            if mobj:
                for router_config in trigger['routers']:
                    router = self.routers[router_config['name']]
                    payload = router.payload(text, cursor, mobj.groupdict(),
                                             **router_config.get('args', {}))
                    router.send(payload)

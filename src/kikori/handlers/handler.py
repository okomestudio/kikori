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

from ..utils import count_lines


log = logging.getLogger(__name__)


def _create_cursor(path, pos, line):
    return SimpleNamespace(path=path, pos=pos, line=line)


def create_message(text, cursor):
    return SimpleNamespace(text=text, cursor=copy.copy(cursor))


class EventHandler(LoggingEventHandler):

    def __init__(self, filename, text_pattern, triggers, routers, **kwargs):
        super(EventHandler, self).__init__(**kwargs)
        self._cache = {}
        self.filename = re.compile(filename)
        self.text_pattern = re.compile(text_pattern)
        self.triggers = [self._load_trigger(t) for t in triggers]
        self.routers = routers

        self._lock = threading.Lock()

    def _load_trigger(self, trigger):
        raise NotImplementedError

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
            log.info('Caching current state of watched file %s: %r',
                     fullpath, cache)

    def _create_cache_entry(self, fullpath, f):
        line = count_lines(f)
        pos = f.tell()
        cursor = _create_cursor(path=fullpath, pos=pos, line=line)
        message = create_message(None, cursor)
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
        """Process a log file when a modified event triggers.

        Args:
            f (stream): A stream object to the modified log file.

        """
        path = self._get_full_path(f.name)

        cursor, message = self._cache[path]
        f.seek(cursor.pos)

        while 1:
            # Read a line from the current position, including the
            # newline at the end
            s = f.readline()

            if s == '':
                # This is effectively an EOF. Although depending on
                # how buffer flush happens, it could be in the middle
                # of multiline log message. Here it is assumed that
                # EOF always contains a full multiline message.
                self._process_message(message)
                message = create_message('', cursor)

                self._cache[path] = cursor, message
                break

            cursor.line += 1
            cursor.pos = f.tell()

            message = self._build_message(cursor, message, s)

    def _build_message(self, cursor, message, line):
        """Build a message from an incoming line.

        Args:
            message: TBD.
            line: An incoming line from the log.

        Returns:
            message

        """
        raise NotImplementedError

    def _match(self, pattern, obj):
        raise NotImplementedError

    def _get_matchable_object(self, obj):
        return obj

    def _render_object(self, obj):
        return obj

    def _process_message(self, message):
        cursor = message.cursor
        obj = self._get_matchable_object(message.text)

        formatted_text = None
        for trigger in self.triggers:
            matched = self._match(trigger['pattern'], obj)
            if matched:
                formatted_text = formatted_text or self._render_object(obj)
                for router_config in trigger['routers']:
                    router = self.routers[router_config['name']]
                    payload = router.payload(formatted_text,
                                             cursor, matched,
                                             **router_config.get('args', {}))
                    router.send(payload)

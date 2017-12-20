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
import argparse
import logging
import time

from .. import config
from ..watchers import EventHandler
from ..watchers import Observer


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def _main(no_hello=False):
    routers = {}
    for k, v in config.conf.get('routers', {}).items():
        if v['type'] == 'slack':
            from kikori.routers.slack import Slack
            router = Slack(v['webhook_url'], **v['args'])
        else:
            raise Exception('Unknown router type')
        if not no_hello:
            router.send_hello()
        routers[k] = router

    observer = Observer()

    for conf in config.conf.get('watch', []):
        dir = conf['dir']
        filename = conf['filename']
        text_pattern = conf['text_pattern']
        triggers = conf['triggers']

        event_handler = EventHandler(filename,
                                     text_pattern,
                                     triggers,
                                     routers)
        event_handler.init(dir)

        observer.schedule(event_handler, dir, recursive=True)

    observer.start()
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        '-c', '--conf', default='conf.yml')
    p.add_argument(
        '--no-hello', action='store_true', default=False)
    args = p.parse_args()

    config.init(args.conf)

    _main(no_hello=args.no_hello)

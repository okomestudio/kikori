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
import logging
import logging.handlers
import random
import threading
import time


logging.basicConfig(
    level='DEBUG',
    filename='tmp/log/error.log',
    format=('%(asctime)s.%(msecs)03d '
            '%(thread)x:%(levelname)s:%(name)s %(message)s'),
    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)


class Logger(threading.Thread):
    def __init__(self):
        super(Logger, self).__init__()
        self.daemon = True
        self.start()

    def run(self):
        while 1:
            p = random.random()
            if p < 0.01:
                try:
                    raise Exception('Something happened')
                except Exception as e:
                    log.exception('Error (%r)', e)
            elif p < 0.03:
                log.warning('I warn you! (%r)' % time.time())
            elif p < 0.07:
                log.info('Some informational message (%r)' % time.time())
            else:
                log.debug('Some debugging message (%r)' % time.time())

            time.sleep(0 + 0.2 * random.random())


def main():
    logger = Logger()
    while 1:
        pass

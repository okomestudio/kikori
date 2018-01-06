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


def filter_json(x, y):
    """Given matching specification `x`, extract matching items from `y`.

    Args:
        x (dict): The matching specification.
        y: A valid JSON object.

    Returns:
        Matched item(s) from y.

    """
    result = {}
    for key, value in x.items():
        if key not in y:
            return None
        if isinstance(value, dict):
            result[key] = filter_json(value, y[key])
        else:
            result[key] = _match_json_value(value, y[key])
    return result


def _match_json_value(x, y):
    if isinstance(x, (int, float)):
        return y if x == y else None
    elif isinstance(x, list):
        raise NotImplementedError
    else:
        # Must be regex match object
        m = x.match(y)
        return m.groupdict() if m else None

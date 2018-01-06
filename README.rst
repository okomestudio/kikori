kikori
======

Kikori is a logging message routing service. It watches log messages
(via `Watchdog <https://github.com/gorakhargosh/watchdog>`_) and
routes ones that matches user-provided patterns to another
destinations. Currently the only supported destination is `Slack
<https://slack.com>`_.

Kikori is licensed under the `MIT License
<https://raw.githubusercontent.com/okomestudio/kikori/development/LICENSE.txt>`_.


Examples
--------

TBD.


App Configuration Specification
-------------------------------

The behavior of kikori is fully controlled by a YAML configuration
file. By default, it looks for ``conf.yml`` in the current directory
(where the service is launched), but it can be stored at an arbitrary
location by the use of ``conf`` switch:

.. code-block:: bash

    $ kikori --conf /path/to/conf.yml
    ... or ...
    $ kikori -c /path/to/conf.yml

The full app config file looks as follows:
    
.. code-block:: yaml

    ---
    routers:
      personal:  # Give a unique name to identify a router
        type: slack
        webhook_url: https://hooks.slack.com/services/XXXXXXXXX/XXX
        args:
          channel: '@username'
      ops:
        type: slack
        webhook_url: https://hooks.slack.com/services/YYYYYYYYY/YYY
        args:
          channel: '#ops'

    watch:
      - dir: /var/log/myservice/
        filename: '.*\.log$'
        text_pattern: ^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+:[A-Z]+:.*
        triggers:
          - pattern: ^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+:ERROR:.*
            routers:
              - name: ops
                args:
                  color: '#ff0000'
                  title: Error logged!
          - pattern: ^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+:WARNING:.*
            routers:
              - name: ops
                args:
                  color: '#ffff00'
                  title: Warning logged!

      - dir: /var/log/myotherservice/
        filename: '.*\.log$'
        text_pattern: ^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+:[A-Z]+:.*
        triggers:
          - pattern: ^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+:(?<level>(ERROR|WARNING)):.*
            routers:
              - name: ops
                args:
                  color: '#ff0000'
                  title: "{level} logged!"
              - name: personal
                args:
                  color: '#ff0000'
                  title: "{level} logged!"


Installation
------------

Kikori runs on Python 3. To install:

.. code-block:: bash

    $ pip install kikori


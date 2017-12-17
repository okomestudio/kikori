kikori
======

Kikori is a logging message routing service. It watches log messages
(via `Watchdog <https://github.com/gorakhargosh/watchdog>`_) and
routes ones that matches user-provided patterns to another
destinations. Currently the only supported destination is `Slack
<https://slack.com>`_.


License
-------

`The MIT License <https://raw.githubusercontent.com/okomestudio/kikori/development/LICENSE.txt>`_


Requirements
------------

- Python 3


Installation
------------

.. code-block:: bash

    $ pip install kikori


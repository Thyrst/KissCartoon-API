KissCartoon API server
======================

Installation
------------

.. code-block:: bash

    $ pip install -r requirements.txt

Example usage with Ngrok
------------------------

In one terminal:

.. code-block:: bash

    $ ngrok http 8000

In another:

.. code-block:: bash

    $ export KISSAPI_HOSTNAME=4e984fa0.ngrok.io
    $ gunicorn kissapi.wsgi -b 127.0.0.1:8000


Environment variables
---------------------

``KISSAPI_HOSTNAME`` is hostname of your server. Default ``localhost``.

``KISSAPI_ORIGINAL_SITE`` is the site with series. Default ``kisscartoon.io``.


Endpoints
---------

Endpoints represent individual functions in API. Each EP recieves the same
GET variables as the function arguments.

Quick overview
^^^^^^^^^^^^^^

- ``newest/``
- ``most_popular/``
- ``recently_added/``

- ``list/``
    - ``first_letter``
    - ``status``
    - ``page``
- ``list_genre/``
    - ``genre``
    - ``page``
- ``search/``
    - ``title``
    - ``genres``
    - ``status``
    - ``page``

- ``series/``
    - ``url``
- ``episode/``
    - ``url``

- ``genres/``
- ``statuses/``


For more information head to `the original documentation <http://kisscartoon-api.rtfd.org>`_

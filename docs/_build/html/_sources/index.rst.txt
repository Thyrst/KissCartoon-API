KissCartoon API's documentation
===============================

KissCartoon is an unofficial API for `kisscartoon.io <http://kisscartoon.io>`_ website.
It's written for Python 3, tested on Python3.6 and Python3.4

.. toctree::
   :hidden:

   reference

Installation
------------

The package is on Pypi, so you can install it simply with ``pip install kisscartoon-api``

Usage
-----

See the :doc:`reference` page.

Need help?
----------

If you have trouble using KissCartoon API, make a new issue on
`the GitHub page of the project <https://github.com/Thyrst/KissCartoon-API>`_
or mail me at ``thyrst@seznam.cz``

Issues
------

Bypass for anti-bot protection doesn't work at 100%, so you'll get a ``BlockedAccess``
error sometimes. I'm working on it.

TODOs
-----

- Sorting lists by sorts categories that are available on the KissCartoon site
  (Sort by alphabet, Sort by popularity, Latest update, New cartoon).
- Logging in
- Get download links of an episode (this will be a tricky one)

Contributing
------------

For testing use `pytest <https://docs.pytest.org/en/latest/>`_: ``pytest tests.py``. Feel free to send a pull request.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

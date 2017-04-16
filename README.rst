.. image:: https://app.codeship.com/projects/f4ea9bc0-04dd-0135-f186-5e3f2d6fab44/status?branch=master

KissCartoon API
===============

This is unofficial API for `kisscartoon.io <http://kisscartoon.io>`_ website.
It's written for Python 3, tested on Python3.6 and Python3.4

Installation
------------

The package is on Pypi, so you can install it simply with ``pip install kisscartoon-api``

Usage
-----

Instructions for use can be found at the webpage of full documentation: `kisscartoon.rtfd.org <http://kisscartoon.rtfd.org>`_


Example of use
--------------

    >>> from KissCartoon import *
    >>> kiss_list = KissCartoon().search('brickleberry')
    >>> for series in kiss_list:
    ...     print(series)
    ...
    Brickleberry Season 01
    Brickleberry Season 03
    Brickleberry Season 02

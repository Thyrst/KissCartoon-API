Reference Guide
===============

This is a brief introduction to all KissCartoon API's features.

Import
------

You'll get all necessary by this import:

``from KissCartoon import KissCartoon, GENRE, STATUS``

.. _kisscartoon:

KissCartoon
-----------

``KissCartoon`` class represent object of a specific page.
As argument you pass URL of a site, default site is `kisscartoon.io <http://kisscartoon.io>`_,
but the domain name can change whenever, what was reason to do it this way.
Also for accesing mirror sites with this API.

With ``KissCartoon`` you can access lists of top ten series that are on the home page.
You can get them with properties ``newest``, ``most_popular`` and ``recently_added``.

    >>> kiss = KissCartoon() # same as KissCartoon('kiscartoon.io')
    >>> print(kiss.newest)
    [   Series(title='Smurfs: The Lost Village', ...),
        Series(title='Leap!', ...),
        Series(title='We Bare Bears Season 3', ...),
        Series(title='Archer - Season 8', ...),
        Series(title='Teen Titans: The Judas Contract', ...),
        Series(title='SpongeBob Sea Side Story (2017)', ...),
        Series(title='Final Fantasy VII: Advent Children Complete', ...),
        Series(title='The Boss Baby (2017)', ...),
        Series(title='Tangled: The Series', ...),
        Series(title='The Grim Adventures of the KND', ...)]

``KissCartoon`` is also used for creating a :ref:`cartoonlist`. There are three methods:
``.search``, ``.list`` and ``.list_genre``: each method returns a :ref:`cartoonlist`.
The difference is that each method allows slightly different filtering of results.

.list method
^^^^^^^^^^^^

``.list`` method takes ``first_letter``, ``status`` and ``page`` as arguments.

:first_letter: Filter series by an initial letter.
:status:
    Filter series by their current status (ongoing/completed).
    You should use predefined constants. See :ref:`constants`.
:page: Set the list to a given page. Default is 1

::

    >>> kiss.list(first_letter='r', status=STATUS.ONGOING)
    CartoonList(url='https://kisscartoon.io/Status/Ongoing/?c=r&', page=1)

.list_genre method
^^^^^^^^^^^^^^^^^^

``.list_genre`` method takes ``genre`` and ``page`` as arguments.

:genre: Filter series by their genre. See :ref:`constants`.
:page: Set the list to a given page. Default is 1

::

    >>> kiss.list_genre(GENRE.ADVENTURE, page=3)
    CartoonList(url='https://kisscartoon.io/Genre/Adventure/?', page=3)

.search method
^^^^^^^^^^^^^^

``.search`` method takes ``title``, ``genres``, ``status`` and ``page`` as arguments.

:title: Search series by their name.
:genres: Search series by their genres. It should be list of wanted genres.)
:status: Search series by their current status (ongoing/completed).
:page: Set the list to a given page. Default is 1

::

    >>> for series in kiss.search('rick', genres=[GENRE.ADVENTURE, GENRE.COMEDY]):
    ...     print(series)
    ...
    Rick and Morty Extras
    Rick and Morty Season 2
    Rick and Morty Season 1
    Rick and Morty - Season 3
    Rick & Steve the Happiest Gay Couple in All the World

.. _cartoonlist:

CartoonList
-----------

``CartoonList`` represents a list of series that is available on the webpage.
We can create list by our own with it's URL. However it's better to use
:ref:`kisscartoon` object which will generate the URL for us.

``CartoonList`` has following attributes:

:url: URL of a list on the current page
:page: Current page
:max_page: Number of pages in a current list
:series: Series on the current page

You can use ``.next`` and ``.back`` methods for navigating through a list.
When you attempt to go beyond the limits (``1`` and``max_page``), method raises
``PaginatorError``:

    >>> from kisscartoon import *
    >>> kiss_list = KissCartoon().list(page=1)
    >>> kiss_list.back()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/thyrst/Tools/kisscartoon/kisscartoon.py", line 356, in back
        raise PaginatorError('No previous page.')
    kisscartoon.PaginatorError: No previous page.

For navigating to any random page, you can use ``.goto`` method which takes
page number as an argument. However, goto won't check if you attempt to go
on an empty page, therefore it's better to use precedent methods.

For getting sum of series on all pages, simply call ``len`` function on a list:

    >>> len(kiss_list)
    4403

``CartoonList`` is a subclass of ``Iterator``, so you can iterate over it:

.. _iterator-example:

    >>> ongoing = 0
    >>> for series in kiss_list:
    ...     if series.status == STATUS.ONGOING:
    ...         ongoing += 1
    ...
    >>> print('Ongoing: %d%%' % (100*ongoing/len(kiss_list)))
    Ongoing: 6%


.. _series:

Series
------

Series represents one season of series. Object has following attributes:

:title: Name of series
:url: URL
:image: URL of image cover
:genres: List of genres of series
:latest_episode: Latest Added episode of series
:episodes: List of :ref:`episode`
:summary: Description of series
:status: Status
:views: Number of views
:aired: A year or date that were series aired

.. _episode:

Episode
-------

Episode object has following attributes:

:title: Title of an episode
:url: URL
:date_added: Date the episode was added to the site (``datetime`` object)
:download_links: Dictionary of links to download episode. This is not implemented yet.

.. _constants:

Constants
---------

You will use these constants for working with :ref:`series` and
for creating :ref:`cartoonlist`. See :ref:`iterator example <iterator-example>`.

Genres
^^^^^^

======================  ============
``GENRE.ACTION``        Action
``GENRE.ADVENTURE``     Adventure
``GENRE.ANIMATION``     Animation
``GENRE.BIOGRAPHY``     Biography
``GENRE.COMEDY``        Comedy
``GENRE.CRIME``         Crime
``GENRE.DOCUMENTARY``   Documentary
``GENRE.DRAMA``         Drama
``GENRE.FAMILY``        Family
``GENRE.FANTASY``       Fantasy
``GENRE.GAMESHOW``      Game-Show
``GENRE.HISTORY``       History
``GENRE.HORROR``        Horror
``GENRE.MOVIE``         Movie
``GENRE.MUSIC``         Music
``GENRE.MUSICAL``       Musical
``GENRE.MYSTERY``       Mystery
``GENRE.PRESCHOOL``     Preschool
``GENRE.ROMANCE``       Romance
``GENRE.SCIFI``         Sci-Fi
``GENRE.SHORT``         Short
``GENRE.SPORT``         Sport
``GENRE.SUPERNATURAL``  Supernatural
``GENRE.THRILLER``      Thriller
``GENRE.WAR``           War
======================  ============

Status
^^^^^^

====================  =========
``STATUS.ONGOING``    Ongoing
``STATUS.COMPLETED``  Completed
====================  =========

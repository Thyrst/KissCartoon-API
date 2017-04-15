#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest import mock
from datetime import datetime
from kisscartoon import KissCartoon, CartoonList, Episode, Series, \
    KissGrab, GENRE, STATUS


class TestConstants(unittest.TestCase):
    def test_genres(self):
        self.assertEqual(GENRE.ACTION, 'Action')
        self.assertEqual(GENRE.ADVENTURE, 'Adventure')
        self.assertEqual(GENRE.BIOGRAPHY, 'Biography')
        self.assertEqual(GENRE.COMEDY, 'Comedy')
        self.assertEqual(GENRE.CRIME, 'Crime')
        self.assertEqual(GENRE.DOCUMENTARY, 'Documentary')
        self.assertEqual(GENRE.DRAMA, 'Drama')
        self.assertEqual(GENRE.FAMILY, 'Family')
        self.assertEqual(GENRE.FANTASY, 'Fantasy')
        self.assertEqual(GENRE.GAMESHOW, 'Game-Show')
        self.assertEqual(GENRE.HISTORY, 'History')
        self.assertEqual(GENRE.HORROR, 'Horror')
        self.assertEqual(GENRE.MOVIE, 'Movie')
        self.assertEqual(GENRE.MUSIC, 'Music')
        self.assertEqual(GENRE.MUSICAL, 'Musical')
        self.assertEqual(GENRE.MYSTERY, 'Mystery')
        self.assertEqual(GENRE.PRESCHOOL, 'Preschool')
        self.assertEqual(GENRE.ROMANCE, 'Romance')
        self.assertEqual(GENRE.SCIFI, 'Sci-Fi')
        self.assertEqual(GENRE.SHORT, 'Short')
        self.assertEqual(GENRE.SPORT, 'Sport')
        self.assertEqual(GENRE.SUPERNATURAL, 'Supernatural')
        self.assertEqual(GENRE.THRILLER, 'Thriller')
        self.assertEqual(GENRE.WAR, 'War')

    def test_statuses(self):
        self.assertEqual(STATUS.ONGOING, ('Ongoing', 'upcoming'))
        self.assertEqual(STATUS.COMPLETED, ('Completed', 'complete'))


class KissCartoonTest(unittest.TestCase):
    def test_default_url(self):
        kiss = KissCartoon()
        self.assertEqual(kiss.url, 'https://kisscartoon.io')

    def test_url(self):
        kiss = KissCartoon('https://kisscartoon.io/')
        self.assertEqual(kiss.url, 'https://kisscartoon.io')
        kiss = KissCartoon('kisscartoon.io')
        self.assertEqual(kiss.url, 'https://kisscartoon.io')

    @mock.patch('kisscartoon.KissGrab')
    def test_top_lists_properties(self, grab):
        url = 'https://kisscartoon.io'
        kiss = KissCartoon(url)
        for prop in ('newest', 'recently_added', 'most_popular'):
            with self.subTest(property=prop):
                with self.assertRaises(AttributeError):
                    setattr(kiss, prop, [])

        kiss._grab.go.assert_not_called()
        self.assertIsInstance(kiss.newest, list)
        kiss._grab.go.assert_called_once()
        kiss._grab.go.assert_called_with(url)
        for prop in ('newest', 'recently_added', 'most_popular'):
            getattr(kiss, prop)
        kiss._grab.go.assert_called_once()

    def test_bad_website(self):
        url = 'invalid.website'
        kiss = KissCartoon(url)
        with self.assertRaises(RuntimeError):
            kiss.newest

    def test_top_lists(self):
        for prop in ('newest', 'recently_added', 'most_popular'):
            kiss = KissCartoon()
            with self.subTest(property=prop):
                top_series = getattr(kiss, prop)
                self.assertEqual(len(top_series), 10, msg='Unable to fetch info from server')
                for series in top_series:
                    self.assertIsInstance(series, Series)
                    self.assertIsInstance(series.title, str)
                    self.assertIsInstance(series.image, str)
                    self.assertIsInstance(series.genres, list)
                    self.assertGreater(len(series.genres), 0)
                    for genre in series.genres:
                        self.assertIsInstance(genre, str)
                        # commented because of errors on server side
                        #self.assertIn(genre, vars(GENRE).values()) # not so correct
                    self.assertTrue(isinstance(series.latest_episode, Episode)
                                    or series.latest_episode is None)

    def test_iterators(self):
        kiss = KissCartoon()

        list1 = kiss.list(page=4)
        self.assertIsInstance(list1, CartoonList)
        self.assertEqual(len(list1.series), 50)

        list2 = kiss.list_genre(GENRE.ACTION)
        self.assertIsInstance(list2, CartoonList)
        self.assertEqual(len(list2.series), 50)

        list3 = kiss.search('and')
        self.assertIsInstance(list3, CartoonList)
        self.assertEqual(len(list3.series), 50)
        with self.assertRaises(RuntimeError):
            list3.back()

        try:
            list1.back()
        except RuntimeError:
            self.assertTrue(False, msg='Back button not found')

        self.assertEqual(list1.page, 3)


class CartoonListTest:
    pass


class SeriesTest(unittest.TestCase):

    def test_empty_init(self):
        with self.assertRaises(TypeError):
            Series()

    def test_attributes(self):
        title = 'Series 1'
        url = 'my url'
        series = Series(KissGrab(), title, url)

        self.assertEqual(series.title, title)
        self.assertEqual(series.url, url)

    def test_calling_update(self):
        grab = mock.Mock()
        grab.doc.tree.xpath.return_value = ''
        episode = 'episode'
        series = Series(grab, 'title', 'url', 'image_url', latest_episode=episode)
        self.assertEqual(series.latest_episode, episode)

        grab.go.assert_not_called()
        self.assertEqual(series.episodes, [])
        grab.go.assert_called_once()

    def test_properties(self):
        grab = KissGrab()
        grab.go('https://kisscartoon.io/Cartoon/Brickleberry-Season-01/')

        grab_mock = mock.Mock()
        grab_mock.doc.tree = grab.doc.tree

        series = Series(
            grab_mock,
            'Brickleberry Season 01',
            'http://kimcartoon.me/Cartoon/Brickleberry-Season-01',
            'http://kimcartoon.me/Uploads/Etc/11-24-2014/2272881brick.jpg'
        )

        self.assertEqual(series.status, STATUS.COMPLETED[0])
        self.assertGreater(series.views, 380000)
        self.assertEqual(series.aired, '2012')
        self.assertEqual(series.genres, [GENRE.COMEDY])
        summary = '''A group of never-do-well forest rangers are facing ''' \
                  '''the shutdown of their National Park when a new ranger ''' \
                  '''arrives to help transform them and save the park.'''
        self.assertEqual(series.summary, summary)
        self.assertEqual(len(series.episodes), 10)
        self.assertTrue(all(isinstance(episode, Episode)) for episode in series.episodes)
        self.assertIsInstance(series.latest_episode, Episode)
        self.assertEqual(series.latest_episode.title,
                         'Watch Brickleberry Season 01 Episode 09 Daddy Issues')
        self.assertEqual(series.latest_episode.date_added, datetime(2014, 11, 25))
        grab_mock.go.assert_called_once()


class EpisodeTest(unittest.TestCase):

    def test_empty_init(self):
        with self.assertRaises(TypeError):
            Episode()

    def test_date_added(self):
        episode = Episode(KissGrab(), 'title', 'url', '4/14/2011')
        self.assertIsInstance(episode.date_added, datetime)
        self.assertEqual(episode.date_added, datetime(2011, 4, 14))

    def test_attributes(self):
        title = 'Episode 1'
        url = 'my url'
        episode = Episode(KissGrab(), title, url)

        self.assertEqual(episode.title, title)
        self.assertEqual(episode.url, url)

    #def test_download_links(self):
    #    episode = Episode(KissGrab(), 'Brickleberry', 'https://kisscartoon.io/Cartoon/Brickleberry-Season-01/Episode-01-Welcome-to-Brickleberry?id=20483')
    #    downloads = OrderedDict(episode.download_links)
    #    self.assertEqual(downloads, OrderedDict())

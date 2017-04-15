#! /usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import js2py
import time
from grab import Grab, error
from copy import copy
from collections.abc import Iterator
from datetime import datetime


class GENRE:
    ACTION = 'Action'
    ADVENTURE = 'Adventure'
    ANIMATION = 'Animation'
    BIOGRAPHY = 'Biography'
    COMEDY = 'Comedy'
    CRIME = 'Crime'
    DOCUMENTARY = 'Documentary'
    DRAMA = 'Drama'
    FAMILY = 'Family'
    FANTASY = 'Fantasy'
    GAMESHOW = 'Game-Show'
    HISTORY = 'History'
    HORROR = 'Horror'
    MOVIE = 'Movie'
    MUSIC = 'Music'
    MUSICAL = 'Musical'
    MYSTERY = 'Mystery'
    PRESCHOOL = 'Preschool'
    ROMANCE = 'Romance'
    SCIFI = 'Sci-Fi'
    SHORT = 'Short'
    SPORT = 'Sport'
    SUPERNATURAL = 'Supernatural'
    THRILLER = 'Thriller'
    WAR = 'War'


class STATUS:
    ONGOING = ('Ongoing', 'upcoming')
    COMPLETED = ('Completed', 'complete')


def elements_to_genres(elements):
    try:
        genres = [element.xpath('@href')[0][7:] for element in elements]
    except IndexError:
        return []
    else:
        return genres

def first(list_):
    try:
        return list_[0]
    except IndexError:
        return ''

def base_url(url):
    try:
        url = str(url)
        url = url.split('//')[-1]
        url = url.split('/', 1)[0]
    except IndexError:
        raise ValueError('Invalid URL')

    url = 'https://' + url
    return url

def absolute_url(base_url, url):
    if not url.startswith(base_url):
        url = base_url.rstrip('/') + '/' + url.lstrip('/')

    return url


class KissGrab(Grab):
    def go(self, url, *args, **kwargs):
        super().go(url, *args, **kwargs)

        check = self.doc.tree.xpath('//h1/span[1]/text()')
        if check and check[0] == 'Checking your browser before accessing':
            try:
                new_url = self._unblock_site(url)
                self.go(new_url, *args, **kwargs)
            except IndexError:
                raise RuntimeError('Can\'t get through antibot protection.')

    def _unblock_site(self, url):
        time.sleep(4)

        tree = self.doc.tree
        url = base_url(url)
        site = url[8:]

        var = tree.xpath('//*[@id="challenge-form"]/input[@name="jschl_vc"]/@value')[0]
        pass_ = tree.xpath('//*[@id="challenge-form"]/input[@name="pass"]/@value')[0]
        js = tree.xpath('//script/text()')[0]

        js = js.split('setTimeout(function(){')[1].split('f.submit();')[0]
        js = [line.strip().lstrip(';') for line in js.split('\n')]
        js.insert(2, ' t = "' + site + '";')
        ret = js[-2].split('a.value =')
        js[-2] = ret[0] + ret[1].split(';')[0]
        js = '\n'.join(line for line in js if line and not line.startswith('a') and not line.startswith('f ') and not line.startswith('t'))

        answer = js2py.eval_js(js)
        unblock_request = absolute_url(url, '/cdn-cgi/l/chk_jschl?jschl_vc=' + var + '&pass=' + pass_ + '&jschl_answer=' + str(answer))

        return unblock_request


class KissCartoon:
    def __init__(self, url='kisscartoon.io'):
        self.url = base_url(url)
        self._grab = KissGrab(connect_timeout=10)
        self._top = {}

    def list(self, first_letter=None, status=None, page=1):
        if status is None:
            url = absolute_url(self.url, '/CartoonList/?')
        else:
            url = absolute_url(self.url, '/Status/' + str(status) + '/?')

        if first_letter:
            url += 'c=' + str(first_letter) + '&'

        return CartoonList(self._grab, url, page)

    def list_genre(self, genre, page=1):
        url = absolute_url(self.url, '/Genre/' + str(genre) + '/?')
        return CartoonList(self._grab, url, page)

    def search(self, title=None, genres=None, status=None, page=1):
        if status is None:
            status = (None, '')

        name = 'name=' + str(title or '')
        genre = 'genre=' + '_'.join(genres or ())
        status = 'status=' + str(status[1])

        searching = '&'.join((name, genre, status))
        url = absolute_url(self.url, '/AdvanceSearch?' + searching + '&')

        return CartoonList(self._grab, url, page)

    def _update_top(self):
        self._grab.go(self.url)
        self._top = {
            'newest': [],
            'recently_added': [],
            'most_popular': [],
        }

        tree = self._grab.doc.tree
        tabs = {
            'newest': tree.xpath('//*[@id="tab-trending"]/div[1]')[0],
            'recently_added': tree.xpath('//*[@id="tab-newest"]/div[1]')[0],
            'most_popular': tree.xpath('//*[@id="tab-mostview"]/div[1]')[0],
        }
        for top, tab in tabs.items():
            for i in range(1, 11):
                image = tab.xpath(f'div[{i}]/a[1]/img/@src')[0]
                image = absolute_url(self.url, image)

                title = tab.xpath(f'div[{i}]/h3/a/span/text()')[0]

                url = tab.xpath(f'div[{i}]/h3/a/@href')[0]
                url = absolute_url(self.url, url)

                genres = tab.xpath(f'div[{i}]/p[1]/a')
                genres = elements_to_genres(genres)

                try:
                    latest_title = tab.xpath(f'div[{i}]/p[2]/a/text()')[0]
                    latest_url = tab.xpath(f'div[{i}]/p[2]/a/@href')[0]
                except IndexError:
                    latest_episode = None
                else:
                    latest_url = absolute_url(self.url, latest_url)
                    latest_episode = Episode(self._grab, latest_title, latest_url)

                series = Series(self._grab, title, url, image, genres, latest_episode)
                self._top[top].append(series)

    def _top_list(self):
        function_name = inspect.stack()[1][3]
        if function_name not in self._top:
            try:
                self._update_top()
            except (IndexError, error.GrabCouldNotResolveHostError):
                raise RuntimeError('Error getting data from server ' + self.url)

        return self._top[function_name]

    @property
    def newest(self):
        return self._top_list()
    @property
    def recently_added(self):
        return self._top_list()
    @property
    def most_popular(self):
        return self._top_list()


class CartoonList(Iterator):
    def __init__(self, grab, url, page=None):
        self._grab = copy(grab)
        self.url = url
        self.series = []
        self._index = 0
        if page is None:
            self.goto(1)
        else:
            self.goto(page)

    def _load_page(self):
        tree = self._grab.doc.tree
        self.series = []
        self._index = 0
        for movie in tree.xpath('//*[@id="leftside"]/div[not(div/text()="Filter cartoon A - Z: ")]/div[2]/div[3]/div')[1:]:
            latest_episode = None
            url = movie.xpath('div[1]/a/@href')[0]
            title = movie.xpath('div[1]/a/descendant-or-self::*/text()')
            title = ' '.join(part.strip() for part in title)
            title = title.strip()

            latest = movie.xpath('div[2]/text()')[0]
            latest = latest.strip()
            if latest == STATUS.COMPLETED[0]:
                status = STATUS.COMPLETED[0]
            else:
                status = STATUS.ONGOING[0]
                try:
                    latest_title = movie.xpath('div[2]/a/text()')[0]
                    latest_url = movie.xpath('div[2]/a/@href')[0]
                except IndexError:
                    pass
                else:
                    latest_episode = Episode(self._grab, latest_title, latest_url)

            series = Series(self._grab, title, url, status=status, latest_episode=latest_episode)
            self.series.append(series)

    def goto(self, page):
        self._grab.go(self.url + 'page=' + str(page))
        self.page = int(page)
        self._load_page()

    def back(self):
        tree = self._grab.doc.tree
        if tree.xpath('//*[@id="leftside"]/div[2]/div[2]/div[4]/ul/li/a[text()="<<"]/@href'):
            self.goto(self.page - 1)
        else:
            raise RuntimeError('No previous page.')

    def next(self):
        tree = self._grab.doc.tree
        if tree.xpath('//*[@id="leftside"]/div[2]/div[2]/div[4]/ul/li/a[text()=">>"]/@href'):
            self.goto(self.page + 1)
        else:
            raise RuntimeError('No next page.')

    def __next__(self):
        try:
            item = self.series[self._index]
        except IndexError:
            try:
                self.next()
            except RuntimeError:
                raise StopIteration()
            else:
                self._index = 0
                item = self.series[self._index]

        self._index += 1
        return item


class Series:
    def __init__(self, grab, title, url, image=None, genres=None,
                 latest_episode=None, episodes=None, summary=None, status=None,
                 views=None, aired=None):
        self._grab = copy(grab)
        self.title = title
        self.url = url
        self.image = image
        self._genres = genres
        self._latest_episode = latest_episode
        self._episodes = episodes
        self._summary = summary
        self._status = status
        self._views = views
        self._aired = aired

    def _update_data(self):
        self._grab.go(self.url)

        tree = self._grab.doc.tree

        genres = tree.xpath('//*[@id="leftside"]/div[1]/div[2]/div[2]/p[1]/a')
        self._genres = elements_to_genres(genres)

        status = ''.join(tree.xpath('//*[@id="leftside"]/div[1]/div[2]/div[2]/div[1]/p[span/text()="Status:"]/text()'))
        self._status = status.strip()

        views = first(tree.xpath('//*[@id="leftside"]/div[1]/div[2]/div[2]/div[1]/p[span/text()="Views:"]/text()'))
        views = views.replace(',', '')
        try:
            self._views = int(views)
        except ValueError:
            pass

        summary = first(tree.xpath('//*[@id="leftside"]/div[1]/div[2]/div[2]/div[@class="summary"]/p/text()'))
        self._summary = summary

        aired = first(tree.xpath('//*[@id="leftside"]/div[1]/div[2]/div[2]/p[span/text()="Date aired:"]/text()[2]'))
        self._aired = aired.strip()

        self._episodes = []
        base_url_ = base_url(self.url)
        for row in tree.xpath('//*[@id="leftside"]/div[2]/div[2]/div[2]/div[2]/div')[1:]:
            try:
                title = row.xpath('div[1]/h3/a/text()')[0].strip()
                url = row.xpath('div[1]/h3/a/@href')[0].strip()
                aired = row.xpath('div[2]/text()')[0].strip()
            except IndexError:
                continue

            url = absolute_url(base_url_, url)
            episode = Episode(self._grab, title, url, aired)
            self._episodes.append(episode)

        try:
            self._latest_episode = self._episodes[0]
        except IndexError:
            pass

    def _get_prop(self):
        function_name = inspect.stack()[1][3]
        if not getattr(self, '_' + function_name):
            self._update_data()

        return getattr(self, '_' + function_name)

    @property
    def genres(self):
        return self._get_prop()
    @property
    def latest_episode(self):
        return self._get_prop()
    @property
    def episodes(self):
        return self._get_prop()
    @property
    def summary(self):
        return self._get_prop()
    @property
    def status(self):
        return self._get_prop()
    @property
    def views(self):
        return self._get_prop()
    @property
    def aired(self):
        return self._get_prop()


class Episode:
    def __init__(self, grab, title, url, date_added=None, download_links=None):
        self._grab = copy(grab)
        self.title = title
        self.url = url
        self.date_added = datetime.strptime(date_added, '%m/%d/%Y') if date_added else None
        self._download_links = download_links or {}

    @property
    def download_links(self):
        if not self._download_links:
            pass
            #self._grab.go(self.url)
            #tree = self._grab.doc.tree
            #
            #for link in tree.xpath('//*[@id="divDownload"]/a'):
            #    try:
            #        key = link.xpath('text()')[0]
            #        value = link.xpath('@href')[0]
            #    except IndexError:
            #        continue
            #
            #    self._download_links[key] = value

        return self._download_links

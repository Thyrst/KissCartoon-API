#! /usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import js2py
import time
from grab import Grab, error
from collections.abc import Iterator
from datetime import datetime


### Helper functions ######################################

def _elements_to_genres(elements):
    ''' Get genre constants from list of `a` elements. '''
    try:
        genres = [element.xpath('@href')[0][7:] for element in elements]
    except IndexError:
        return []
    else:
        return genres

def _first(list_):
    try:
        return list_[0]
    except IndexError:
        return ''

def _base_url(url):
    ''' Method for making base url in format `https://domain.name` '''
    try:
        url = str(url)
        url = url.split('//')[-1]
        url = url.split('/', 1)[0]
    except IndexError:
        raise ValueError('Invalid URL')

    url = 'https://' + url
    return url

def _absolute_url(base_url, url):
    ''' Safe method for building absolute url from links '''
    if not url.startswith(base_url):
        url = base_url.rstrip('/') + '/' + url.lstrip('/')

    return url


### Constants #############################################

class GENRE:
    ''' Genres available on kisscartoon.io '''

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
    '''
    Status of a cartoon. Each constant is a tuple of two strings.
    First string is used in URL, second is used for searching.
    '''
    ONGOING = 'Ongoing'
    COMPLETED = 'Completed'


### Helper objects ########################################

class BlockedAccess(RuntimeError):
    '''
    Exception raised when page couldn't be fetched due to Anti-Bot protection
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class KissGrab(Grab):
    '''
    Wrapper around original `grab` (see http://docs.grablib.org/en/latest/).
    It's customized for kisscartoon.io which sometimes check if client
    is a common user with browser, so this client has to bypass it.
    '''
    def __init__(self, *args, **kwargs):
        if 'connect_timeout' not in kwargs:
            kwargs['connect_timeout'] = 10

        super().__init__(*args, **kwargs)

    def go(self, url, *args, **kwargs):
        for _ in range(2):
            try:
                super().go(url, *args, **kwargs)
                if self._check():
                    try:
                        new_url = self._unblock_site(url)
                        super().go(new_url, *args, **kwargs)
                    except IndexError:
                        raise BlockedAccess()
                    if self._check():
                        raise BlockedAccess()
                else:
                    break
            except BlockedAccess:
                time.sleep(2)
                continue
            else:
                break
        else:
            raise BlockedAccess('Can\'t get through anti-bot protection.')

    def _check(self):
        check = self.doc.tree.xpath('//h1/span[1]/text()')
        anti_bot = (check and check[0] == 'Checking your browser before accessing')
        return anti_bot

    def _unblock_site(self, url):
        ''' TODO: This doesn't work for 100% '''
        time.sleep(4)

        tree = self.doc.tree
        url = _base_url(url)
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
        unblock_request = _absolute_url(url, '/cdn-cgi/l/chk_jschl?jschl_vc=' + var + '&pass=' + pass_ + '&jschl_answer=' + str(answer))

        return unblock_request


### Main objects ##########################################

class KissCartoon:
    '''
    KissCartoon main object serves to generating lists of series
    with help of `.search`, `.list` or `.list_genre` methods.

    It also contains list of top ten newest, most popular and recently updated series.
    '''
    def __init__(self, url='kisscartoon.io'):
        self.url = _base_url(url)
        self._grab = KissGrab()
        self._top = {}

    def list(self, first_letter=None, status=None, page=1):
        if status is None:
            url = _absolute_url(self.url, '/CartoonList/?')
        else:
            url = _absolute_url(self.url, '/Status/' + str(status or '') + '/?')

        if first_letter:
            url += 'c=' + str(first_letter) + '&'

        return CartoonList(url, page)

    def list_genre(self, genre, page=1):
        url = _absolute_url(self.url, '/Genre/' + str(genre) + '/?')
        return CartoonList(url, page)

    def search(self, title=None, genres=None, status=None, page=1):
        if status is STATUS.COMPLETED:
            status = 'complete'
        elif status is STATUS.ONGOING:
            status = 'upcoming'
        elif status is None:
            status = None
        else:
            raise ValueError('Invalid status argument.')

        name = 'name=' + str(title or '')
        genre = 'genre=' + '_'.join(genres or ())
        status = 'status=' + str(status or '')

        searching = '&'.join((name, genre, status))
        url = _absolute_url(self.url, '/AdvanceSearch?' + searching + '&')

        return CartoonList(url, page)

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
                image = tab.xpath('div[{}]/a[1]/img/@src'.format(i))[0]
                image = _absolute_url(self.url, image)

                title = tab.xpath('div[{}]/h3/a/span/text()'.format(i))[0]

                url = tab.xpath('div[{}]/h3/a/@href'.format(i))[0]
                url = _absolute_url(self.url, url)

                genres = tab.xpath('div[{}]/p[1]/a'.format(i))
                genres = _elements_to_genres(genres)

                try:
                    latest_title = tab.xpath('div[{}]/p[2]/a/text()'.format(i))[0]
                    latest_url = tab.xpath('div[{}]/p[2]/a/@href'.format(i))[0]
                except IndexError:
                    latest_episode = None
                else:
                    latest_url = _absolute_url(self.url, latest_url)
                    latest_episode = Episode(latest_title, latest_url)

                series = Series(title, url, image, genres, latest_episode)
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

    def __repr__(self):
        repr_ = 'KissCartoon(url={!r})'.format(self.url)
        return repr_

class PaginatorError(Exception):
    pass

class CartoonList(Iterator):
    '''
    List of series. It can be used as an iterator.
    It is possible to navigate through list pages with
    `.next`, `.back` and `.goto` methods.
    '''
    def __init__(self, url, page=None):
        self._grab = KissGrab()
        self.url = url
        self.series = []
        self._index = 0
        if page is None:
            self.goto(1)
        else:
            self.goto(page)
        self.max_page = self._get_max_page()
        self._len = self._get_length()

    def _get_max_page(self):
        tree = self._grab.doc.tree
        max_page = tree.xpath('//*[@id="leftside"]/div[not(div/text()="Filter cartoon A - Z: ")]/div[2]/div[4]/ul/li[not(a/text()=">>")][last()]/a/text()')
        try:
            max_page = max_page[0]
            max_page = int(max_page)
        except (IndexError, ValueError):
            max_page = 1

        return max_page

    def _get_length(self):
        tree = self._grab.doc.tree
        info = tree.xpath('//*[@id="leftside"]/div[not(div/text()="Filter cartoon A - Z: ")]/div[2]/div[4]/ul/p/text()')
        try:
            items_len = info[0]
            items_len = items_len.split('of', 1)[1].split('item', 1)[0]
            items_len = items_len.replace(',', '')
            items_len = int(items_len)
        except (IndexError, ValueError):
            items_len = len(self.series)

        return items_len

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
            if latest == STATUS.COMPLETED:
                status = STATUS.COMPLETED
            else:
                status = STATUS.ONGOING
                try:
                    latest_title = movie.xpath('div[2]/a/text()')[0]
                    latest_url = movie.xpath('div[2]/a/@href')[0]
                except IndexError:
                    pass
                else:
                    latest_episode = Episode(latest_title, latest_url)

            series = Series(title, url, status=status, latest_episode=latest_episode)
            self.series.append(series)

    def goto(self, page):
        self._grab.go(self.url + 'page=' + str(page))
        self.page = int(page)
        self._load_page()

    def back(self):
        if self.page > 1:
            self.goto(self.page - 1)
        else:
            raise PaginatorError('No previous page.')

    def next(self):
        if self.page < self.max_page:
            self.goto(self.page + 1)
        else:
            raise PaginatorError('No next page.')

    def __next__(self):
        try:
            item = self.series[self._index]
        except IndexError:
            try:
                self.next()
            except PaginatorError:
                raise StopIteration()
            else:
                self._index = 0
                item = self.series[self._index]

        self._index += 1
        return item

    def __len__(self):
        return self._len

    def __repr__(self):
        data = (self.url, self.page)
        repr_ = 'CartoonList(url={!r}, page={!r})'.format(*data)
        return repr_


class Series:
    '''
    Class that contains information about a given series.
    '''
    def __init__(self, title, url, image=None, genres=None,
                 latest_episode=None, episodes=None, summary=None, status=None,
                 views=None, aired=None):
        self._grab = KissGrab()
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
        self._genres = _elements_to_genres(genres)

        # sometimes this fails in tests. dunno why
        status = _first(tree.xpath('//*[@id="leftside"]/div[1]/div[2]/div[2]/div[1]/p[span/text()="Status:"]/text()'))
        self._status = status.strip()

        views = _first(tree.xpath('//*[@id="leftside"]/div[1]/div[2]/div[2]/div[1]/p[span/text()="Views:"]/text()'))
        views = views.replace(',', '')
        try:
            self._views = int(views)
        except ValueError:
            pass

        summary = _first(tree.xpath('//*[@id="leftside"]/div[1]/div[2]/div[2]/div[@class="summary"]/p/text()'))
        self._summary = summary

        aired = _first(tree.xpath('//*[@id="leftside"]/div[1]/div[2]/div[2]/p[span/text()="Date aired:"]/text()[2]'))
        self._aired = aired.strip()

        self._episodes = []
        base_url = _base_url(self.url)
        for row in tree.xpath('//*[@id="leftside"]/div[2]/div[2]/div[2]/div[2]/div')[1:]:
            try:
                title = row.xpath('div[1]/h3/a/text()')[0].strip()
                url = row.xpath('div[1]/h3/a/@href')[0].strip()
                aired = row.xpath('div[2]/text()')[0].strip()
            except IndexError:
                continue

            url = _absolute_url(base_url, url)
            episode = Episode(title, url, aired)
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

    def __str__(self):
        return self.title

    def __repr__(self):
        data = (self.title, self.url, self.image)
        repr_ = 'Series(title={!r}, url={!r}, image={!r})'.format(*data)
        return repr_


class Episode:
    '''
    Class that contains information about a given episode.
    '''
    def __init__(self, title, url, date_added=None, download_links=None):
        self._grab = KissGrab()
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

    def __str__(self):
        return self.title

    def __repr__(self):
        date = self.date_added.strftime('%m/%d/%Y') if self.date_added else None
        data = (self.title, self.url, date, self.download_links)
        repr_ = 'Episode(title={!r}, url={!r}, date_added={!r}, download_links={!r})'.format(*data)
        return repr_

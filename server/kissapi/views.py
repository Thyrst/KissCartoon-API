from datetime import datetime, timedelta

from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from KissCartoon import KissCartoon, Series, GENRE, STATUS


def _to_dict(obj):
    return {x: y for x, y in obj.__dict__.items() if not x.startswith('_')}


class MainView(APIView):

    def get(self, request):
        error = None
        now = datetime.now()

        data = settings.CACHE['data']
        updated = settings.CACHE['updated']

        if not data or (now - updated) > timedelta(hours=1):
            settings.CACHE['updated'] = now

            kiss = KissCartoon(settings.ORIGINAL_SITE)
            try:
                settings.CACHE['data'] = {
                    'newest': kiss.newest,
                    'most_popular': kiss.most_popular,
                    'recently_added': kiss.recently_added
                }
            except RuntimeError as e:
                error = [str(e)]

        if error:
            response = Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            tab = request.path.strip('/')
            series = settings.CACHE['data'][tab or 'newest']

            response = Response([_to_dict(s) for s in series])

        return response


class ListView(APIView):

    def get(self, request):
        first_letter = request.GET.get('first_letter')
        status = request.GET.get('status')

        try:
            page = int(request.GET.get('page', 1))
        except ValueError as e:
            raise ValidationError(str(e))

        kiss = KissCartoon(settings.ORIGINAL_SITE)
        cartoon_list = kiss.list(first_letter=first_letter,
                                 status=status, page=page)

        series = [_to_dict(s) for s in cartoon_list.series]
        return Response(series)


class ListGenreView(APIView):

    def get(self, request):
        genre = request.GET.get('genre')

        try:
            page = int(request.GET.get('page', 1))
        except ValueError as e:
            raise ValidationError(str(e))

        kiss = KissCartoon(settings.ORIGINAL_SITE)
        cartoon_list = kiss.list_genre(genre=genre, page=page)

        series = [_to_dict(s) for s in cartoon_list.series]
        return Response(series)


class SearchView(APIView):

    def get(self, request):
        title = request.GET.get('title')
        status = request.GET.get('status')
        genres = request.GET.get('genres', '').split(',')

        try:
            page = int(request.GET.get('page', 1))
        except ValueError as e:
            raise ValidationError(str(e))

        kiss = KissCartoon(settings.ORIGINAL_SITE)
        cartoon_list = kiss.search(title=title, genres=genres,
                                   status=status, page=page)

        series = [_to_dict(s) for s in cartoon_list.series]
        return Response(series)


class SeriesView(APIView):

    def get(self, request):
        url = request.GET.get('url')

        series = Series(title='', url=url)
        series = {
            'genres': series.genres,
            'latest_episode': _to_dict(series.latest_episode),
            'episodes': [_to_dict(e) for e in series.episodes],
            'summary': series.summary,
            'status': series.status,
            'views': series.views,
            'aired': series.aired
        }

        return Response(series)


class EpisodeView(APIView):

    def get(self, request):
        error = ['Not implemented.']
        return Response(error, status=status.HTTP_501_NOT_IMPLEMENTED)


class GenreView(APIView):

    def get(self, request):
        return Response(_to_dict(GENRE))


class StatusView(APIView):

    def get(self, request):
        return Response(_to_dict(STATUS))

from django.conf.urls import url
from kissapi.views import MainView, ListView, ListGenreView, SearchView, \
    SeriesView, EpisodeView, GenreView, StatusView


urlpatterns = [
    url(r'^$', MainView.as_view()),
    url(r'^newest/$', MainView.as_view()),
    url(r'^most_popular/$', MainView.as_view()),
    url(r'^recently_added/$', MainView.as_view()),
    url(r'^list/$', ListView.as_view()),
    url(r'^list_genre/$', ListGenreView.as_view()),
    url(r'^search/$', SearchView.as_view()),

    url(r'^series/$', SeriesView.as_view()),
    url(r'^episode/$', EpisodeView.as_view()),

    url(r'^genres/$', GenreView.as_view()),
    url(r'^statuses/$', StatusView.as_view()),
]

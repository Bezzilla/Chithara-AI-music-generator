from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('songs/generate/', views.GenerateSongView.as_view(), name='song-generate'),
    path('songs/<uuid:song_id>/download/', views.SongDownloadView.as_view(), name='song-download'),
]

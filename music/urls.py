from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('songs/generate/', views.GenerateSongView.as_view(), name='song-generate'),
    path('songs/<uuid:song_id>/download/', views.SongDownloadView.as_view(), name='song-download'),
    path('songs/<uuid:song_id>/visibility/', views.SongVisibilityView.as_view(), name='song-visibility'),
    path('songs/<uuid:song_id>/update/', views.SongUpdateView.as_view(), name='song-update'),
    path('songs/<uuid:song_id>/delete/', views.SongDeleteView.as_view(), name='song-delete'),
    path('songs/<uuid:song_id>/save/', views.SaveSongView.as_view(), name='song-save'),
    path('albums/create/', views.AlbumCreateView.as_view(), name='album-create'),
    path('albums/<uuid:album_id>/update/', views.AlbumUpdateView.as_view(), name='album-update'),
    path('albums/<uuid:album_id>/delete/', views.AlbumDeleteView.as_view(), name='album-delete'),
    path('albums/<uuid:album_id>/songs/', views.AlbumSongView.as_view(), name='album-songs'),
]

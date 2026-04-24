from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from music import views as music_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('music.urls')),
    path('', lambda request: redirect('login'), name='home'),
    path('login/', music_views.login_view, name='login'),
    path('logout/', music_views.logout_view, name='logout'),
    path('dashboard/', music_views.dashboard_view, name='dashboard'),
]

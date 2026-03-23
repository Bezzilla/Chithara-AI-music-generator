from django.contrib import admin
from .models import User, Song, Album, ShareLink


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("display_name", "email", "created_at")
    search_fields = ("display_name", "email")


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "genre", "occasion", "visibility", "created_at")
    list_filter = ("genre", "occasion", "visibility")
    search_fields = ("title", "owner__display_name")


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at")
    search_fields = ("title", "owner__display_name")
    filter_horizontal = ("songs",)


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ("link_id", "song", "album", "created_at")
import uuid
from django.db import models
from .choices import Visibility
from .user import User
from .song import Song


class Album(models.Model):
    album_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title      = models.CharField(max_length=255)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE)
    created_at = models.DateTimeField(auto_now_add=True)
    owner      = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    songs      = models.ManyToManyField(Song, related_name="albums", blank=True)

    class Meta:
        db_table = "album"

    def __str__(self):
        return f"{self.title} (owned by {self.owner.display_name})"

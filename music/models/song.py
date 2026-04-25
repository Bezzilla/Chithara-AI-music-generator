import uuid
from django.db import models
from .choices import Genre, Occasion, Visibility, SongStatus
from .user import User


class Song(models.Model):
    song_id     = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title       = models.CharField(max_length=255)
    occasion    = models.CharField(max_length=20, choices=Occasion.choices)
    description = models.TextField(blank=True)
    genre       = models.CharField(max_length=20, choices=Genre.choices)
    duration    = models.FloatField(null=True, blank=True)
    visibility  = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE)
    audio_url   = models.URLField(max_length=1024, null=True, blank=True)
    status      = models.CharField(max_length=10, choices=SongStatus.choices, default=SongStatus.PENDING)
    task_id     = models.CharField(max_length=255, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    owner       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="songs")

    class Meta:
        db_table = "song"

    def __str__(self):
        return f"{self.title} by {self.owner.display_name}"

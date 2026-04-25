import uuid
from django.db import models
from django.core.exceptions import ValidationError


class Genre(models.TextChoices):
    POP = "POP", "Pop"
    ROCK = "ROCK", "Rock"
    JAZZ = "JAZZ", "Jazz"
    CLASSICAL = "CLASSICAL", "Classical"
    HIP_HOP = "HIP_HOP", "Hip Hop"
    OTHER = "OTHER", "Other"


class Occasion(models.TextChoices):
    BIRTHDAY = "BIRTHDAY", "Birthday"
    WEDDING = "WEDDING", "Wedding"
    GRADUATION = "GRADUATION", "Graduation"
    HOLIDAY = "HOLIDAY", "Holiday"
    OTHER = "OTHER", "Other"


class Visibility(models.TextChoices):
    PUBLIC = "PUBLIC", "Public"
    PRIVATE = "PRIVATE", "Private"
    INVITE = "INVITE", "Invite Only"


class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user"

    def __str__(self):
        return f"{self.display_name} ({self.email})"


class SongStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUCCESS = "SUCCESS", "Success"
    FAILED  = "FAILED",  "Failed"


class Song(models.Model):
    song_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title     = models.CharField(max_length=255)
    occasion  = models.CharField(max_length=20, choices=Occasion.choices)
    description = models.TextField(blank=True)
    genre     = models.CharField(max_length=20, choices=Genre.choices)
    duration  = models.FloatField(null=True, blank=True)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE)
    audio_url = models.URLField(max_length=1024, null=True, blank=True)
    status    = models.CharField(max_length=10, choices=SongStatus.choices, default=SongStatus.PENDING)
    task_id   = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="songs")

    class Meta:
        db_table = "song"

    def __str__(self):
        return f"{self.title} by {self.owner.display_name}"


class Album(models.Model):
    album_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    songs = models.ManyToManyField(Song, related_name="albums", blank=True)

    class Meta:
        db_table = "album"

    def __str__(self):
        return f"{self.title} (owned by {self.owner.display_name})"


class ShareLink(models.Model):
    link_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, blank=True, related_name="share_links")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True, related_name="share_links")

    class Meta:
        db_table = "share_link"

    def clean(self):
        if self.song is None and self.album is None:
            raise ValidationError("A ShareLink must reference either a Song or an Album.")
        if self.song is not None and self.album is not None:
            raise ValidationError("A ShareLink cannot reference both a Song and an Album.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        target = self.song or self.album
        return f"ShareLink → {target}"


class SavedSong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_songs')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_song'
        unique_together = [('user', 'song')]

    def __str__(self):
        return f"{self.user.display_name} saved {self.song.title}"
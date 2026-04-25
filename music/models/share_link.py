import uuid
from django.db import models
from django.core.exceptions import ValidationError
from .song import Song
from .album import Album


class ShareLink(models.Model):
    link_id    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url        = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    song       = models.ForeignKey(Song,  on_delete=models.CASCADE, null=True, blank=True, related_name="share_links")
    album      = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True, related_name="share_links")

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

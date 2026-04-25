from django.db import models
from .user import User
from .song import Song


class SavedSong(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_songs')
    song     = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table       = 'saved_song'
        unique_together = [('user', 'song')]

    def __str__(self):
        return f"{self.user.display_name} saved {self.song.title}"

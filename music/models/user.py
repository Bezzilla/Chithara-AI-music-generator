import uuid
from django.db import models


class User(models.Model):
    user_id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email        = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=128, blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user"

    def __str__(self):
        return f"{self.display_name} ({self.email})"

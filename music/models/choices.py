from django.db import models


class Genre(models.TextChoices):
    POP       = "POP",       "Pop"
    ROCK      = "ROCK",      "Rock"
    JAZZ      = "JAZZ",      "Jazz"
    CLASSICAL = "CLASSICAL", "Classical"
    HIP_HOP   = "HIP_HOP",  "Hip Hop"
    OTHER     = "OTHER",     "Other"


class Occasion(models.TextChoices):
    BIRTHDAY   = "BIRTHDAY",   "Birthday"
    WEDDING    = "WEDDING",    "Wedding"
    GRADUATION = "GRADUATION", "Graduation"
    HOLIDAY    = "HOLIDAY",    "Holiday"
    OTHER      = "OTHER",      "Other"


class Visibility(models.TextChoices):
    PUBLIC  = "PUBLIC",  "Public"
    PRIVATE = "PRIVATE", "Private"
    INVITE  = "INVITE",  "Invite Only"


class SongStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUCCESS = "SUCCESS", "Success"
    FAILED  = "FAILED",  "Failed"

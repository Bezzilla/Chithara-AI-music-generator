from django.dispatch import receiver
from allauth.account.signals import user_logged_in


@receiver(user_logged_in)
def sync_music_user(request, user, **kwargs):
    from music.models import User as MusicUser
    display_name = user.get_full_name() or user.email.split('@')[0]
    music_user, _ = MusicUser.objects.get_or_create(
        email=user.email,
        defaults={'display_name': display_name},
    )
    request.session['user_id'] = str(music_user.user_id)

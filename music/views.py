import json
import uuid
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import logout as auth_logout
from .models import User, Song, Album, ShareLink, SavedSong
from .services.generation_service import SongGenerationContext


def login_view(request):
    if request.session.get('user_id'):
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        from django.contrib.auth.hashers import make_password, check_password
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        else:
            try:
                user = User.objects.get(email__iexact=email)
                if user.password_hash:
                    if not check_password(password, user.password_hash):
                        error = 'Incorrect password.'
                    else:
                        request.session['user_id'] = str(user.user_id)
                        return redirect('dashboard')
                else:
                    # Google OAuth user — set password and log in
                    user.password_hash = make_password(password)
                    user.save()
                    request.session['user_id'] = str(user.user_id)
                    return redirect('dashboard')
            except User.DoesNotExist:
                display_name = email.split('@')[0]
                user = User.objects.create(
                    email=email,
                    display_name=display_name,
                    password_hash=make_password(password),
                )
                request.session['user_id'] = str(user.user_id)
                return redirect('dashboard')
    return render(request, 'music/login.html', {'error': error})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


def dashboard_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')
    all_songs = Song.objects.filter(owner=user).order_by('-created_at')
    albums = Album.objects.filter(owner=user).prefetch_related('songs')
    discover_songs = (
        Song.objects.filter(visibility='PUBLIC', status='SUCCESS')
        .select_related('owner')
        .order_by('-created_at')[:60]
    )
    saved_ids = set(
        SavedSong.objects.filter(user=user).values_list('song_id', flat=True)
    )
    return render(request, 'music/dashboard.html', {
        'user': user,
        'songs': all_songs[:10],
        'all_songs': all_songs,
        'albums': albums,
        'discover_songs': discover_songs,
        'saved_ids': saved_ids,
    })


@method_decorator(csrf_exempt, name="dispatch")
class UserListView(View):
    def get(self, request):
        users = list(User.objects.values("user_id", "email", "display_name", "created_at"))
        return JsonResponse(users, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class GenerateSongView(View):
    def post(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Not authenticated.'}, status=401)
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

        title = body.get('title', '').strip()
        occasion = body.get('occasion', '').strip()
        genre = body.get('genre', '').strip()
        description = body.get('description', '').strip()

        if not title:
            return JsonResponse({'error': 'Title is required.'}, status=400)
        if not occasion:
            return JsonResponse({'error': 'Occasion is required.'}, status=400)
        if not genre:
            return JsonResponse({'error': 'Genre is required.'}, status=400)

        song = Song.objects.create(
            title=title,
            occasion=occasion,
            genre=genre,
            description=description,
            owner=user,
        )

        try:
            context = SongGenerationContext()
            song = context.generate(song)
        except Exception as e:
            song.status = 'FAILED'
            song.save()
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({
            'song_id': str(song.song_id),
            'title': song.title,
            'status': song.status,
            'audio_url': song.audio_url,
            'duration': song.duration,
        }, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class SongVisibilityView(View):
    def post(self, request, song_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Not authenticated.'}, status=401)
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        try:
            song = Song.objects.get(song_id=song_id, owner__user_id=user_id)
        except Song.DoesNotExist:
            return JsonResponse({'error': 'Song not found.'}, status=404)
        visibility = body.get('visibility', 'PRIVATE')
        if visibility not in ('PUBLIC', 'PRIVATE', 'INVITE'):
            return JsonResponse({'error': 'Invalid visibility.'}, status=400)
        song.visibility = visibility
        song.save()
        response_data = {'visibility': song.visibility}
        if visibility == 'INVITE':
            share_link = song.share_links.first()
            if not share_link:
                link_id = uuid.uuid4()
                share_link = ShareLink(link_id=link_id, url=f'/share/{link_id}/', song=song)
                share_link.save()
            response_data['share_url'] = share_link.url
        return JsonResponse(response_data)


def share_view(request, link_id):
    try:
        share_link = ShareLink.objects.select_related('song__owner').get(link_id=link_id)
    except ShareLink.DoesNotExist:
        raise Http404
    song = share_link.song
    if not song or song.visibility != 'INVITE':
        raise Http404

    viewer = None
    is_owner = False
    is_saved = False
    user_id = request.session.get('user_id')
    if user_id:
        try:
            viewer = User.objects.get(user_id=user_id)
            is_owner = (str(song.owner_id) == str(viewer.user_id))
            if not is_owner:
                is_saved = SavedSong.objects.filter(user=viewer, song=song).exists()
        except User.DoesNotExist:
            pass

    return render(request, 'music/share.html', {
        'song': song,
        'viewer': viewer,
        'is_owner': is_owner,
        'is_saved': is_saved,
    })


@method_decorator(csrf_exempt, name="dispatch")
class SongDeleteView(View):
    def post(self, request, song_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Not authenticated.'}, status=401)
        try:
            song = Song.objects.get(song_id=song_id, owner__user_id=user_id)
        except Song.DoesNotExist:
            return JsonResponse({'error': 'Song not found.'}, status=404)
        song.delete()
        return JsonResponse({'deleted': True})


@method_decorator(csrf_exempt, name="dispatch")
class SongUpdateView(View):
    def post(self, request, song_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Not authenticated.'}, status=401)
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        try:
            song = Song.objects.get(song_id=song_id, owner__user_id=user_id)
        except Song.DoesNotExist:
            return JsonResponse({'error': 'Song not found.'}, status=404)
        title = body.get('title', '').strip()
        if not title:
            return JsonResponse({'error': 'Title cannot be empty.'}, status=400)
        song.title = title
        song.save()
        return JsonResponse({'title': song.title})


@method_decorator(csrf_exempt, name="dispatch")
class SaveSongView(View):
    def post(self, request, song_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Not authenticated.'}, status=401)
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
        try:
            song = Song.objects.get(song_id=song_id)
        except Song.DoesNotExist:
            return JsonResponse({'error': 'Song not found.'}, status=404)
        if str(song.owner_id) == str(user.user_id):
            return JsonResponse({'error': 'You already own this song.'}, status=400)
        _, created = SavedSong.objects.get_or_create(user=user, song=song)
        return JsonResponse({'saved': True, 'already_saved': not created})


class SongDownloadView(View):
    def get(self, request, song_id):
        try:
            song = Song.objects.get(song_id=song_id)
        except Song.DoesNotExist:
            raise Http404

        if not song.audio_url:
            return JsonResponse({'error': 'Audio not ready yet.'}, status=404)

        import urllib.request
        req = urllib.request.Request(song.audio_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            content = response.read()

        filename = f"{song.title.replace(' ', '_')}.mp3"
        http_response = HttpResponse(content, content_type='audio/mpeg')
        http_response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return http_response

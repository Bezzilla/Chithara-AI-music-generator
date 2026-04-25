import json
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import logout as auth_logout
from .models import User, Song, Album
from .services.generation_service import SongGenerationContext


def login_view(request):
    if request.session.get('user_id'):
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        display_name = request.POST.get('display_name', '').strip()
        if not email:
            error = 'Email is required.'
        else:
            if not display_name:
                display_name = email.split('@')[0]
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={'display_name': display_name}
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
    songs = Song.objects.filter(owner=user).order_by('-created_at')[:10]
    albums = Album.objects.filter(owner=user)[:5]
    return render(request, 'music/dashboard.html', {
        'user': user,
        'songs': songs,
        'albums': albums,
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

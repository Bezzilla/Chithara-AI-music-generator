import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, Song, Album


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
    request.session.flush()
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

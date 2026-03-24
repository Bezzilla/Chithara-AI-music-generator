import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User


@method_decorator(csrf_exempt, name="dispatch")
class UserListView(View):
    def get(self, request):
        users = list(User.objects.values("user_id", "email", "display_name", "created_at"))
        return JsonResponse(users, safe=False)

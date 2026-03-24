import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User


def _json_body(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}


@method_decorator(csrf_exempt, name="dispatch")
class UserListView(View):
    def get(self, request):
        users = list(User.objects.values("user_id", "email", "display_name", "created_at"))
        return JsonResponse(users, safe=False)

    def post(self, request):
        data = _json_body(request)
        user = User.objects.create(
            email=data["email"],
            display_name=data["display_name"],
        )
        return JsonResponse({"user_id": str(user.user_id), "email": user.email}, status=201)
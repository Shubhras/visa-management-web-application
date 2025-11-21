import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile


@csrf_exempt
def users_api(request):
    if request.method == 'GET':
        users = UserProfile.objects.all().values()
        return JsonResponse(list(users),safe = False)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        users = UserProfile.objects.create(
           name = data.get('name'),
           email = data.get('email'),
           age = data.get('age')
        )
        return JsonResponse({"message":"user created ", "id" : users.id})
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SupportRoom


def chats(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # Pobieranie wszystkich pokoi czatu przypisanych do bieżącego użytkownika
    user = request.user
    rooms = SupportRoom.objects.filter(user=user)

    # Przekazywanie pokoji do szablonu
    return render(request, 'support/chats.html', {'section': 'support', 'rooms': rooms})


@csrf_exempt
def create_room(request):
    if request.method == "POST":
        data = json.loads(request.body)
        room_title = data.get("title")

        if not room_title:
            return JsonResponse({"error": "Room title is required"}, status=400)

        room = SupportRoom.objects.create(title=room_title, user=request.user)
        return JsonResponse({"uuid": room.uuid, "title": room.title, "status": room.status}, status=201)
    
    else:
        return HttpResponse("404")
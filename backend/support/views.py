from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from .models import SupportRoom


def chats(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # Pobieranie wszystkich pokoi czatu przypisanych do bieżącego użytkownika
    user = request.user
    rooms = SupportRoom.objects.filter(user=user)

    # Przekazywanie pokoji do szablonu
    return render(request, 'support/chats.html', {'rooms': rooms})

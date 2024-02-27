import json
from django.shortcuts import render
from django.utils.safestring import mark_safe
from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ads.models import Car
from chat.forms import LoginForm
from chat.models import Chat
from chat.serializers import ChatSerializer
from chat.utils import get_or_create_chat_with_users, generate_unique_room_name
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth import authenticate, login


class UserLogin(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "chat/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd.get('username'), password=cd.get('password'))
            if user is not None:
                login(request, user)

            else:
                form.add_error("username", "Invalid username or password")
        else:
            form.add_error("username", "Invalid data")
        return render(request, "chat/login.html", {"form": form})


def index(request):
    return render(request, "chat/index.html")

def room(request, room_name):
    username = request.user.username
    context = {
        'room_name': room_name,
        'username': mark_safe(json.dumps(username))

    }
    return render(request, "chat/room.html", context)


class CurrentUserDefaultFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(users=request.user)


class ListRoomsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    filter_backends = (CurrentUserDefaultFilter,)


class LeaveRoomAPIView(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            roomName = request.data.get('roomName')
            chat = Chat.objects.get(roomName=roomName)
            user = request.user
            chat.users.remove(user)
            chat.save()
            return Response({'success': True, "message": "you have left the room successfully"})
        else:
            return Response({'success': False, "message": "you are not authenticated"})


class JoinRoomAPIView(APIView):
    def get(self, request, car, *args, **kwargs):
        if request.user.is_authenticated:
            car = Car.objects.get(id=car)
            seller, user = car.user, request.user
            chat = get_or_create_chat_with_users(seller, user)

            return Response({'success': True, "roomName": {chat.roomName}})
        else:
            return Response({'success': False, "message": "you are not authenticated"})

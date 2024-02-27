# chat/urls.py
from django.urls import path
from chat.views import *
from django.contrib.auth import views
app_name = 'chat'
urlpatterns = [
    path("", index, name="index"),
    path('login', views.LoginView.as_view(template_name='chat/login.html'), name="login"),
    path("<str:room_name>/", room, name="room"),
    path('api/list', ListRoomsAPIView.as_view(), name='list-rooms'),
    path('api/join/<int:car>', JoinRoomAPIView.as_view(), name='join-room'),
    path('api/leave', LeaveRoomAPIView.as_view(), name='leave-room'),
]
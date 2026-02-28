from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path("", views.chat_list, name="chat_list"),
    path("find/", views.find_or_create_chat, name="find_or_create_chat"),
    path("start/<int:seller_id>/", views.start_chat_with_seller, name="start_chat"),
    path("room/<uuid:room_id>/", views.chat_room, name="chat_room"),
    path("api/room/<uuid:room_id>/messages/", views.load_more_messages, name="load_messages"),
]
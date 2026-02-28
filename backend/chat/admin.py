from django.contrib import admin
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "seller", "created_at")
    list_filter = ("created_at",)
    search_fields = ("buyer__username", "seller__username")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "sender", "text", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text", "sender__username", "room__id")
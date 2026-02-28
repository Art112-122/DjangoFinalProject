from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import JsonResponse
from chat.models import ChatRoom
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@login_required
def chat_list(request):
    rooms_as_buyer = ChatRoom.objects.filter(buyer=request.user).select_related('seller')
    rooms_as_seller = ChatRoom.objects.filter(seller=request.user).select_related('buyer')

    all_rooms = []
    for room in rooms_as_buyer:
        last_message = room.messages.order_by("-created_at").first()
        unread_count = (
            room.messages.filter(is_read=False).exclude(sender=request.user).count()
        )

        all_rooms.append(
            {
                "room": room,
                "other_user": room.seller,
                "last_message": last_message,
                "unread_count": unread_count,  # Передаем в шаблон
            }
        )

    for room in rooms_as_seller:
        last_message = room.messages.order_by('-created_at').first()
        all_rooms.append({
            'room': room,
            'other_user': room.buyer,
            'last_message': last_message
        })

    all_rooms.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else x['room'].created_at,
                   reverse=True)

    paginator = Paginator(all_rooms, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'chat/chat_list.html', {'page_obj': page_obj, 'rooms': page_obj})


@login_required
def start_chat_with_seller(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)

    if request.user == seller:
        messages.error(request, 'Вы не можете начать чат с самим собой.')
        return redirect('chat:chat_list')
    room = ChatRoom.objects.filter(
        (Q(buyer=request.user) & Q(seller=seller)) |
        (Q(buyer=seller) & Q(seller=request.user))
    ).first()
    if not room:
        room = ChatRoom.objects.create(buyer=request.user, seller=seller)
        logger.info(f"Создан новый чат ID {room.id} между {request.user} и {seller}")

    return redirect('chat:chat_room', room_id=room.id)


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom.objects.select_related('buyer', 'seller'), id=room_id)

    room.messages.filter(is_read=False).exclude(sender=request.user).update(
        is_read=True
    )
    
    if request.user not in [room.buyer, room.seller]:
        messages.error(request, 'Нет доступа к чату')
        return redirect('chat:chat_list')

    messages_list = room.messages.select_related('sender').order_by('-created_at')
    paginator = Paginator(messages_list, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    other_user = room.seller if request.user == room.buyer else room.buyer

    context = {
        "room": room,
        "messages": page_obj.object_list,
        "page_obj": page_obj,
        "user_id": request.user.id,
        "other_user": other_user,
        "room_id": room_id,
    }
    return render(request, "chat/chat_room.html", context)


@login_required
def load_more_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.user not in [room.buyer, room.seller]:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    page = int(request.GET.get('page', 1))
    messages_list = room.messages.select_related('sender').order_by('-created_at')
    paginator = Paginator(messages_list, 50)

    if page > paginator.num_pages:
        return JsonResponse({'messages': [], 'has_next': False})

    page_obj = paginator.get_page(page)

    messages_data = [{
        'id': msg.id,
        'text': msg.text,
        'sender': msg.sender.username,
        'sender_id': msg.sender.id,
        'created_at': msg.created_at.isoformat(),
        'is_own': msg.sender_id == request.user.id
    } for msg in page_obj]

    return JsonResponse({
        'messages': messages_data,
        'has_next': page_obj.has_next(),
        'next_page': page + 1 if page_obj.has_next() else None
    })
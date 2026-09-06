import json

from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import Conversation, Message
from .services.matcher import find_best_answer

MAX_MESSAGE_LENGTH = 500


def register(request):
    if request.user.is_authenticated:
        return redirect("chat_page")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("chat_page")
    else:
        form = UserCreationForm()

    return render(request, "chatbot/register.html", {"form": form})


class ChatbotLoginView(LoginView):
    template_name = "chatbot/login.html"
    authentication_form = AuthenticationForm


class ChatbotLogoutView(LogoutView):
    next_page = "login"




@login_required
def chat_page(request):
    conversations = Conversation.objects.filter(user=request.user)
    return render(request, "chatbot/chat.html", {"conversations": conversations})




def _message_to_dict(message: Message) -> dict:
    return {
        "id": str(message.id),
        "sender": message.sender,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
    }


def _conversation_to_dict(conversation: Conversation) -> dict:
    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
    }




@login_required
@require_http_methods(["GET", "POST"])
def conversations_view(request):
    if request.method == "POST":
        conversation = Conversation.objects.create(user=request.user, title="New chat")
        return JsonResponse(_conversation_to_dict(conversation), status=201)

    # GET: list only the logged-in user's own conversations.
    conversations = Conversation.objects.filter(user=request.user)
    data = [_conversation_to_dict(c) for c in conversations]
    return JsonResponse({"conversations": data}, status=200)


@login_required
@require_http_methods(["GET"])
def get_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
    except Conversation.DoesNotExist:
        # Same response for "does not exist" and "belongs to someone else"
        # so we don't leak whether the id exists at all.
        return JsonResponse({"error": "Conversation not found."}, status=404)

    messages = conversation.messages.all()
    data = _conversation_to_dict(conversation)
    data["messages"] = [_message_to_dict(m) for m in messages]
    return JsonResponse(data, status=200)




@login_required
@require_http_methods(["POST"])
def send_message(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
    except Conversation.DoesNotExist:
        return JsonResponse({"error": "Conversation not found."}, status=404)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Request body must be valid JSON."}, status=400)

    content = (payload.get("content") or "").strip()

    if not content:
        return JsonResponse({"error": "Message cannot be empty."}, status=400)
    if len(content) > MAX_MESSAGE_LENGTH:
        return JsonResponse(
            {"error": f"Message is too long (max {MAX_MESSAGE_LENGTH} characters)."},
            status=400,
        )

    with transaction.atomic():
        user_message = Message.objects.create(
            conversation=conversation, sender=Message.Sender.USER, content=content
        )

        # Use the first user message as the conversation title.
        if conversation.messages.filter(sender=Message.Sender.USER).count() == 1:
            conversation.title = content[:50]
            conversation.save(update_fields=["title"])

        answer = find_best_answer(content)

        bot_message = Message.objects.create(
            conversation=conversation, sender=Message.Sender.BOT, content=answer
        )

    return JsonResponse(
        {
            "user_message": _message_to_dict(user_message),
            "bot_message": _message_to_dict(bot_message),
        },
        status=201,
    )

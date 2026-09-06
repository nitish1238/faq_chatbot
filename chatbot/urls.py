from django.urls import path

from . import views

urlpatterns = [
    # Pages
    path("register/", views.register, name="register"),
    path("login/", views.ChatbotLoginView.as_view(), name="login"),
    path("logout/", views.ChatbotLogoutView.as_view(), name="logout"),
    path("", views.chat_page, name="chat_page"),
    # API
    # GET (list) and POST (create) both live on this same URL — see views.py
    path("api/conversations/", views.conversations_view, name="api_conversations"),
    path(
        "api/conversations/<uuid:conversation_id>/",
        views.get_conversation,
        name="api_get_conversation",
    ),
    path(
        "api/conversations/<uuid:conversation_id>/messages/",
        views.send_message,
        name="api_send_message",
    ),
]

from django.contrib import admin

from .models import FAQ, Conversation, Message


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("question", "answer", "keywords")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at")
    list_filter = ("user",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "content", "created_at")
    list_filter = ("sender",)

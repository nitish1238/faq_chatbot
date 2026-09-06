import uuid

from django.conf import settings
from django.db import models


class FAQ(models.Model):
   

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    keywords = models.CharField(
        max_length=500,
        help_text="Comma-separated keywords used for matching, e.g. 'refund,return,money back'",
    )
    category = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "question"]

    def __str__(self):
        return self.question


class Conversation(models.Model):
    """One chat 'session' belonging to a single user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    title = models.CharField(max_length=100, default="New chat")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.user})"


class Message(models.Model):
    """A single message inside a conversation — either from the USER or the BOT."""

    class Sender(models.TextChoices):
        USER = "USER", "User"
        BOT = "BOT", "Bot"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=4, choices=Sender.choices)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.sender}] {self.content[:40]}"

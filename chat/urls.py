# chat/urls.py
from django.urls import path
from .views import ChatHistoryView, ChatView

urlpatterns = [
    # Returns all chat sessions for the authenticated user
    path("history/", ChatHistoryView.as_view(), name="chat-history"),

    # Send a message to the chatbot and get a response
    path("send/", ChatView.as_view(), name="chat-send"),
]

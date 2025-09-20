from django.urls import path
from .views import ChatHistoryView, ChatView

urlpatterns = [
    path("history/", ChatHistoryView.as_view(), name="chat-history"),
    path("send/", ChatView.as_view(), name="chat"),
]

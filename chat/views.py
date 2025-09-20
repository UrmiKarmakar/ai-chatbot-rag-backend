from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .services import rag_service
import logging

logger = logging.getLogger(__name__)


class ChatHistoryView(generics.ListAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            ChatSession.objects.filter(user=self.request.user)
            .prefetch_related("messages")
        )


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    session_id = serializers.IntegerField(required=False)


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.validated_data["message"]
        session_id = serializer.validated_data.get("session_id")

        # session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({"error": "Chat session not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            session = ChatSession.objects.create(user=request.user)

        # save user message
        user_msg = ChatMessage.objects.create(session=session, role="user", content=user_message)

        # RAG
        try:
            rag_result = rag_service.process_query(user_message, session.id)
            ai_response = rag_result.get("response", "No response generated.")
        except Exception as e:
            logger.error("RAG service failed: %s", e, exc_info=True)
            ai_response = "Sorry, I had trouble generating a response. Please try again later."
            rag_result = {}

        # save assistant message
        ai_msg = ChatMessage.objects.create(session=session, role="assistant", content=ai_response)

        if not session.title:
            session.title = user_message[:50] + ("..." if len(user_message) > 50 else "")
            session.save(update_fields=["title"])

        return Response(
            {
                "session": ChatSessionSerializer(session).data,
                "user_message": ChatMessageSerializer(user_msg).data,
                "assistant_message": ChatMessageSerializer(ai_msg).data,
                "rag_metadata": rag_result,
            },
            status=status.HTTP_200_OK,
        )

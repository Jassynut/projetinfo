from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Question
from .serializers_api import QuestionDetailSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """
    CRUD basique des questions pour compatibilité frontend
    """

    queryset = Question.objects.all().order_by('question_code')
    serializer_class = QuestionDetailSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        # autoriser multipart pour image
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


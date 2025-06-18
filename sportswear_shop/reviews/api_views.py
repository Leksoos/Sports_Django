from typing import Any
from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer

class ReviewListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint для просмотра списка отзывов и создания нового отзыва.
    Разрешения: аутентификация не обязательна для чтения, обязательна для создания.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer: ReviewSerializer) -> None:
        """
        Сохраняет новый отзыв с привязкой к текущему пользователю.
        """
        serializer.save(user=self.request.user)

class ReviewRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint для получения, обновления и удаления конкретного отзыва.
    Разрешения: аутентификация не обязательна для чтения, обязательна для изменения.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

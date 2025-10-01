from rest_framework import viewsets, generics, permissions, status
from courses.permissions import IsOwnerOrStaff, IsNotModer, IsModerOrOwnerOrStaff
from courses.serializers import CourseSerializer, LessonSerializer
from django.db.models import Count, Prefetch, Exists, OuterRef
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Lesson, Subscription


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer

    def get_permissions(self):
        # Базовое требование: JWT
        if self.action in ("list", "retrieve"):
            # смотреть: модерам любой объект; немодерам — фильтруем в get_queryset
            perms = [permissions.IsAuthenticated]
        elif self.action in ("update", "partial_update"):
            # редактировать: модератор ИЛИ владелец/staff
            perms = [permissions.IsAuthenticated, IsModerOrOwnerOrStaff]
        elif self.action == "create":
            # модераторам создавать нельзя
            perms = [permissions.IsAuthenticated, IsNotModer]
        elif self.action == "destroy":
            # модераторам удалять нельзя; только владелец/staff
            perms = [permissions.IsAuthenticated, IsOwnerOrStaff]
        else:
            perms = [permissions.IsAuthenticated]
        return [p() if isinstance(p, type) else p for p in perms]

    def get_queryset(self):
        qs = (
            Course.objects
            .annotate(lesson_count=Count("lessons", distinct=True))
            .prefetch_related(
                Prefetch(
                    "lessons",
                    queryset=Lesson.objects.only("id", "title", "description", "link", "course_id").order_by("id")
                )
            )
            .order_by("id")
        )

        user = self.request.user
        if user.is_authenticated:
            # Аннотируем признак подписки без N+1
            subs = Subscription.objects.filter(course_id=OuterRef("pk"), user_id=user.id)
            qs = qs.annotate(_is_subscribed=Exists(subs))

            # Немодератор видит только свои курсы
            if not user.groups.filter(name="moderators").exists() and not user.is_staff:
                qs = qs.filter(owner=user)

        return qs

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def subscription(self, request, pk=None):
        """
        POST /api/v1/course/<id>/subscription/
        Тоггл подписки текущего пользователя на курс.
        """
        course_item = self.get_object()
        qs = Subscription.objects.filter(user=request.user, course=course_item)

        if qs.exists():
            qs.delete()
            return Response(
                {"message": "подписка удалена", "course": course_item.id, "is_subscribed": False},
                status=status.HTTP_200_OK
            )

        Subscription.objects.get_or_create(user=request.user, course=course_item)
        return Response(
            {"message": "подписка добавлена", "course": course_item.id, "is_subscribed": True},
            status=status.HTTP_200_OK
        )


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotModer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Lesson.objects.all()
        user = self.request.user
        # Немодератор видит только свои уроки
        if user.is_authenticated and not user.groups.filter(name="moderators").exists() and not user.is_staff:
            return qs.filter(owner=user)
        return qs


class LessonRetrieveApiView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsModerOrOwnerOrStaff]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsModerOrOwnerOrStaff]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

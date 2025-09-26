from django.urls import path

from courses.apps import CoursesConfig
from rest_framework.routers import DefaultRouter

from courses.views import CourseViewSet, LessonListAPIView, LessonCreateAPIView, LessonUpdateAPIView, \
    LessonRetrieveApiView, LessonDestroyAPIView

app_name = CoursesConfig.name


router = DefaultRouter()
router.register(r'course', CourseViewSet,basename='course')

urlpatterns = [
    path('lesson/', LessonListAPIView.as_view(), name='lesson-list'),
    path('lesson/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
    path('lesson/<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lesson/<int:pk>/', LessonRetrieveApiView.as_view(), name='lesson-detail'),
    path('lesson/<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
] + router.urls
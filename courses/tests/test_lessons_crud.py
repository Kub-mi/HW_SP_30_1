from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, Lesson

User = get_user_model()


class LessonCRUDTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moderators = Group.objects.create(name="moderators")

        # Пользователи (ВАЖНО: добавляем username)
        cls.owner = User.objects.create_user(username="owner", email="owner@example.com", password="pass", first_name="Owner")
        cls.other = User.objects.create_user(username="other", email="other@example.com", password="pass", first_name="Other")
        cls.moder = User.objects.create_user(username="moder", email="moder@example.com", password="pass", first_name="Moder")
        cls.staff = User.objects.create_user(username="staff", email="staff@example.com", password="pass", first_name="Staff", is_staff=True)
        cls.moder.groups.add(cls.moderators)

        # Курс владельца
        cls.course = Course.objects.create(title="Course A", description="Desc", owner=cls.owner)

        # Уроки
        cls.owner_lesson = Lesson.objects.create(
            course=cls.course, title="L1", description="d1", link="https://www.youtube.com/watch?v=abc",
            owner=cls.owner
        )
        cls.other_lesson = Lesson.objects.create(
            course=cls.course, title="L2", description="d2", link="https://www.youtube.com/watch?v=def",
            owner=cls.other
        )

        # URL names
        cls.lesson_list_url = reverse("courses:lesson-list")
        cls.lesson_create_url = reverse("courses:lesson-create")

    # ----- LIST -----
    def test_list_as_owner_sees_only_own_lessons(self):
        self.client.force_authenticate(self.owner)
        resp = self.client.get(self.lesson_list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in resp.data.get("results", resp.data)]
        self.assertIn(self.owner_lesson.id, ids)
        self.assertNotIn(self.other_lesson.id, ids)

    def test_list_as_moderator_sees_all(self):
        self.client.force_authenticate(self.moder)
        resp = self.client.get(self.lesson_list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in resp.data.get("results", resp.data)]
        self.assertIn(self.owner_lesson.id, ids)
        self.assertIn(self.other_lesson.id, ids)

    def test_list_as_staff_sees_all(self):
        self.client.force_authenticate(self.staff)
        resp = self.client.get(self.lesson_list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in resp.data.get("results", resp.data)]
        self.assertIn(self.owner_lesson.id, ids)
        self.assertIn(self.other_lesson.id, ids)

    # ----- CREATE -----
    def test_create_lesson_non_moderator_ok_owner_assigned(self):
        self.client.force_authenticate(self.owner)
        payload = {
            "course": self.course.id,
            "title": "New L",
            "description": "d",
            "link": "https://www.youtube.com/watch?v=xyz"
        }
        resp = self.client.post(self.lesson_create_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        lesson_id = resp.data["id"]
        obj = Lesson.objects.get(pk=lesson_id)
        self.assertEqual(obj.owner, self.owner)

    def test_create_lesson_moderator_forbidden(self):
        self.client.force_authenticate(self.moder)
        payload = {
            "course": self.course.id,
            "title": "New L",
            "description": "d",
            "link": "https://www.youtube.com/watch?v=xyz"
        }
        resp = self.client.post(self.lesson_create_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ----- UPDATE -----
    def test_update_lesson_owner_ok(self):
        self.client.force_authenticate(self.owner)
        url = reverse("courses:lesson-update", args=[self.owner_lesson.id])
        resp = self.client.patch(url, {"title": "L1-edit"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.owner_lesson.refresh_from_db()
        self.assertEqual(self.owner_lesson.title, "L1-edit")

    def test_update_lesson_moderator_ok(self):
        self.client.force_authenticate(self.moder)
        url = reverse("courses:lesson-update", args=[self.owner_lesson.id])
        resp = self.client.patch(url, {"title": "moder-edit"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_lesson_other_user_forbidden(self):
        self.client.force_authenticate(self.other)
        url = reverse("courses:lesson-update", args=[self.owner_lesson.id])
        resp = self.client.patch(url, {"title": "hacker"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ----- DELETE -----
    def test_delete_lesson_owner_ok(self):
        self.client.force_authenticate(self.owner)
        url = reverse("courses:lesson-delete", args=[self.owner_lesson.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.owner_lesson.id).exists())

    def test_delete_lesson_moderator_forbidden(self):
        self.client.force_authenticate(self.moder)
        url = reverse("courses:lesson-delete", args=[self.other_lesson.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_staff_ok(self):
        self.client.force_authenticate(self.staff)
        url = reverse("courses:lesson-delete", args=[self.other_lesson.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.other_lesson.id).exists())

    # ----- (необязательно) валидатор ссылки -----
    def test_create_lesson_with_non_youtube_link_rejected(self):
        self.client.force_authenticate(self.owner)
        payload = {
            "course": self.course.id,
            "title": "Bad link",
            "description": "d",
            "link": "https://udemy.com/whatever"
        }
        resp = self.client.post(self.lesson_create_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("link", resp.data)
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, Subscription

User = get_user_model()


class SubscriptionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="u", email="u@example.com", password="pass", first_name="U")
        # один раз достаточно
        cls.course = Course.objects.create(title="Course S", description="Desc", owner=cls.user)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_toggle_subscription_add_and_remove(self):
        url = reverse("courses:course-subscription", args=[self.course.id])

        # 1) Подписаться
        resp1 = self.client.post(url)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertTrue(resp1.data["is_subscribed"])
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # 2) Отписаться
        resp2 = self.client.post(url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertFalse(resp2.data["is_subscribed"])
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_is_subscribed_flag_in_detail_and_list(self):
        # Подписаться
        self.client.post(reverse("courses:course-subscription", args=[self.course.id]))

        # DETAIL
        d = self.client.get(reverse("courses:course-detail", args=[self.course.id]))
        self.assertEqual(d.status_code, status.HTTP_200_OK)
        self.assertTrue(d.data["is_subscribed"])

        # LIST
        lst = self.client.get(reverse("courses:course-list"))
        self.assertEqual(lst.status_code, status.HTTP_200_OK)
        results = lst.data.get("results", lst.data)
        self.assertTrue(any(item["id"] == self.course.id and item["is_subscribed"] for item in results))

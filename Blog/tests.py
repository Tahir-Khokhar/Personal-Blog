from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from Blog import models as Blog_models

User = get_user_model()

EMAIL_OVERRIDE = override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locale.EmailBackend")


@EMAIL_OVERRIDE
class AuthAndPermissionTests(APITestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            email="a@example.com", full_name="Alice", password="Str0ng!pass")
        self.u2 = User.objects.create_user(
            email="b@example.com", full_name="Bob", password="Str0ng!pass")
        self.cat = Blog_models.Category.objects.create(title="Tech")
        self.post = Blog_models.Post.objects.create(
            user=self.u1, title="Hello World", description="body",
            category=self.cat, status="Active")

    def _auth(self, user):
        self.client.force_authenticate(user=user)

    def test_register_requires_password_match(self):
        url = reverse("auth_register")
        resp = self.client.post(url, {
            "full_name": "C", "email": "c@example.com",
            "password": "Str0ng!pass", "password2": "different"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_creates_user(self):
        url = reverse("auth_register")
        resp = self.client.post(url, {
            "full_name": "C", "email": "c@example.com",
            "password": "Str0ng!pass", "password2": "Str0ng!pass"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="c@example.com").exists())

    def test_profile_requires_auth(self):
        url = reverse("user_profile")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_own_profile_only(self):
        self._auth(self.u2)
        url = reverse("user_profile")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["user"]["email"], "b@example.com")

    def test_cannot_edit_others_post(self):
        self._auth(self.u2)
        url = reverse("post_detail", args=[self.post.id])
        resp = self.client.patch(url, {"title": "hacked"}, format="json")
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN,
                                         status.HTTP_404_NOT_FOUND))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Hello World")

    def test_owner_can_edit_own_post(self):
        self._auth(self.u1)
        url = reverse("post_detail", args=[self.post.id])
        resp = self.client.patch(url, {"title": "Updated"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated")

    def test_comment_list_scoped_to_author(self):
        Blog_models.Comment.objects.create(
            post=self.post, name="X", email="x@x.com", comment="hi")
        self._auth(self.u2)  # not the author
        url = "/author/dashboard/comment-list/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 0)

    def test_password_reset_confirm_rejects_bad_token(self):
        url = reverse("password_reset_confirm")
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes(self.u1.pk))
        resp = self.client.post(url, {
            "email": uidb64, "token": "bad", "password": "New!pass1",
            "password2": "New!pass1"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ModelTests(APITestCase):
    def test_profile_auto_created(self):
        u = User.objects.create_user(
            email="p@example.com", full_name="P", password="Str0ng!pass")
        self.assertTrue(Blog_models.Profile.objects.filter(user=u).exists())

    def test_unique_bookmark(self):
        u = User.objects.create_user(
            email="u@example.com", full_name="U", password="Str0ng!pass")
        c = Blog_models.Category.objects.create(title="C")
        p = Blog_models.Post.objects.create(
            user=u, title="P", description="d", category=c)
        Blog_models.Bookmark.objects.create(user=u, post=p)
        with self.assertRaises(Exception):
            Blog_models.Bookmark.objects.create(user=u, post=p)

    def test_slug_generated_and_unique(self):
        u = User.objects.create_user(
            email="s@example.com", full_name="S", password="Str0ng!pass")
        c = Blog_models.Category.objects.create(title="C")
        p1 = Blog_models.Post.objects.create(
            user=u, title="Same", description="d", category=c)
        p2 = Blog_models.Post.objects.create(
            user=u, title="Same", description="d", category=c)
        self.assertTrue(p1.slug)
        self.assertNotEqual(p1.slug, p2.slug)

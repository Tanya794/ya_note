from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create(username='Person Owner')
        cls.note1 = Note.objects.create(
            title='None1',
            text='Text for note1',
            slug='note-1',
            author=cls.owner
        )

    def test_pages_availability(self):
        urls = (
            'users:login',
            'users:logout',
            'users:signup',
            'notes:home'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_detail_list_edit_delete_add_done(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note1.slug,)),
            ('notes:detail', (self.note1.slug,)),
            ('notes:delete', (self.note1.slug,)),
            ('notes:list', None),
            ('notes:success', None)
        )
        self.client.force_login(self.owner)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note1.slug,)),
            ('notes:detail', (self.note1.slug,)),
            ('notes:delete', (self.note1.slug,)),
            ('notes:list', None),
            ('notes:success', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Note 1'
    NOTE_TEXT = 'Note text'
    NOTE_SLUG = 'note-1'

    @classmethod
    def setUpTestData(cls):
        cls.add_note_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.owner = User.objects.create(username='Person Owner')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.owner)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.add_note_url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.add_note_url,
                                         data=self.form_data)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.owner)

    def test_slug_must_be_unique(self):
        self.auth_client.post(self.add_note_url, data=self.form_data)
        response = self.auth_client.post(self.add_note_url,
                                         data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors='note-1' + WARNING
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Note Title'
    NEW_NOTE_TITLE = 'New Note Title'

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create(username='Person Owner')
        cls.owner_client = Client()
        cls.owner_client.force_login(cls.owner)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text='some text',
            author=cls.owner
        )
        cls.note_ulr = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.note.text
        }

    def test_owner_can_delete_note(self):
        response = self.owner_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_somebody_cant_delete_note_but_owner(self):
        response = self.client.delete(self.delete_url)
        self.assertRedirects(response,
                             f'{self.login_url}?next={self.delete_url}')
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_owner_can_edit_note(self):
        response = self.owner_client.post(self.edit_url, self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)

    def test_somebody_cant_edit_note_but_owner(self):
        response = self.client.post(self.edit_url, self.form_data)
        self.assertRedirects(response,
                             f'{self.login_url}?next={self.edit_url}')
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)

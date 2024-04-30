from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_notes = reverse('notes:list')
        cls.new_note_url = reverse('notes:add')
        cls.owner = User.objects.create(username='Person')
        cls.notes = [
            Note(
                title=f'Note {i}',
                text=f'text of note {i}',
                slug=f'note-{i}',
                author=cls.owner
            )
            for i in range(7)
        ]
        Note.objects.bulk_create(cls.notes)

    def test_order_of_notes(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url_notes)
        object_list = response.context['object_list']
        notes_id = [note.id for note in object_list]
        check_list = [i+1 for i in range(7)]
        self.assertEqual(notes_id, check_list)

    def test_form_page(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.new_note_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

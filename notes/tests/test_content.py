from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


class NoteListViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

        self.note = Note.objects.create(
            title='Test Note',
            text='This is a test note',
            slug='test-note',
            author=self.user,
        )

    def test_note_list_view(self):
        self.client.login(username='testuser', password='testpassword')

        url = reverse('notes:list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertIn(self.note, response.context['object_list'])


class NotesListTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password2'
        )

        self.note1 = Note.objects.create(
            title='Заметка 1', text='Текст заметки 1', author=self.user1
        )
        self.note2 = Note.objects.create(
            title='Заметка 2', text='Текст заметки 2', author=self.user2
        )

    def test_notes_list_only_contains_user_notes(self):
        self.client.login(username='user1', password='password1')

        url = reverse('notes:list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        notes = response.context['object_list']
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0], self.note1)


class NoteCreateUpdateFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_note_create_form(self):
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_update_form(self):
        note = Note.objects.create(
            title='Test Note', text='Test text', author=self.user
        )

        response = self.client.get(
            reverse('notes:edit', kwargs={'slug': note.slug})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response.context['form'], NoteForm)
        self.assertEqual(response.context['form'].instance, note)

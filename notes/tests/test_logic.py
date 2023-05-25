from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


class NoteCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_authenticated_user_can_create_note(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(
            reverse('notes:add'),
            {'title': 'Test Note', 'text': 'This is a test note.'},
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.first()

        self.assertEqual(note.author, self.user)

    def test_anonymous_user_cannot_create_note(self):
        response = self.client.post(
            reverse('notes:add'),
            {'title': 'Test Note', 'text': 'This is a test note.'},
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)


class NoteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.note = Note.objects.create(
            title='Test Note',
            text='This is a test note',
            slug='1',
            author=self.user,
        )

    def test_duplicate_slug_creation(self):
        duplicate_note_data = {
            'title': 'Duplicate Note',
            'text': 'This is a duplicate note',
            'slug': '1',
        }
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('notes:add'), data=duplicate_note_data
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response,
            'form',
            'slug',
            '1 - такой slug уже существует, придумайте уникальное значение!',
        )


class NoteTestSlugIsNotFilled(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')

    def test_slug_auto_generation(self):
        response = self.client.post(
            reverse('notes:add'),
            {'title': 'Test Note', 'text': 'This is a test note'},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.get(title='Test Note')
        self.assertTrue(note.slug)


class NoteTestDeleteEdit(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password2'
        )

        # Создаем заметки
        self.note1 = Note.objects.create(
            title='Note 1', text='Text 1', author=self.user1
        )
        self.note2 = Note.objects.create(
            title='Note 2', text='Text 2', author=self.user2
        )

        self.client = Client()

    def test_edit_own_note(self):
        self.client.login(username='user1', password='password1')

        url = reverse('notes:edit', kwargs={'slug': self.note1.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = {
            'title': 'Updated Note',
            'text': 'Updated Text',
            'slug': 'updated-note',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        updated_note = Note.objects.get(id=self.note1.id)
        self.assertEqual(updated_note.title, 'Updated Note')
        self.assertEqual(updated_note.text, 'Updated Text')

    def test_edit_other_user_note(self):
        self.client.login(username='user1', password='password1')

        url = reverse('notes:edit', kwargs={'slug': self.note2.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_own_note(self):
        self.client.login(username='user1', password='password1')

        url = reverse('notes:delete', kwargs={'slug': self.note1.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(id=self.note1.id).exists())

    def test_delete_other_user_note(self):
        self.client.login(username='user1', password='password1')

        url = reverse('notes:delete', kwargs={'slug': self.note2.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

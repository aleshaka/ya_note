from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


class NoteTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user1 = User.objects.create_user(
            username='user1',
            password='password1'
        )
        cls.user2 = User.objects.create_user(
            username='user2',
            password='password2'
        )

    def setUp(self):
        self.note1 = Note.objects.create(
            title='Note 1',
            text='Text 1',
            author=self.user1,
            slug='1',
        )
        self.note2 = Note.objects.create(
            title='Note 2',
            text='Text 2',
            author=self.user2,
            slug='2',
        )

    def test_authenticated_user_can_create_note(self):
        """
        Проверка что залогиненный пользователь может создать заметку.
        """
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('notes:add'),
            {'title': 'Test Note', 'text': 'This is a test note.'},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 3)
        note = Note.objects.last()
        self.assertEqual(note.author, self.user1)
        self.assertEqual(note.title, 'Test Note')
        self.assertEqual(note.text, 'This is a test note.')

    def test_anonymous_user_cannot_create_note(self):
        """
        Проверка что анонимный пользователь не может создать заметку.
        """
        response = self.client.post(
            reverse('notes:add'),
            {'title': 'Test Note', 'text': 'This is a test note.'},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 2)

    def test_slug_auto_generation(self):
        """
        Проверка автоматического формирования slug.
        """
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('notes:add'),
            {'title': 'Test Note', 'text': 'This is a test note'},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.get(title='Test Note')
        self.assertTrue(note.slug)

    def test_edit_own_note(self):
        """
        Проверка что пользователь может редактировать свои заметки.
        """
        self.client.force_login(self.user1)
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
        """
        Проверка что пользователь не может редактировать чужие заметки.
        """
        self.client.force_login(self.user1)
        url = reverse('notes:edit', kwargs={'slug': self.note2.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_own_note(self):
        """
        Проверка что пользователь может удалять свои заметки.
        """
        self.client.force_login(self.user1)
        url = reverse('notes:delete', kwargs={'slug': self.note1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(id=self.note1.id).exists())

    def test_delete_other_user_note(self):
        """
        Проверка что пользователь не может удалять чужие заметки.
        """
        self.client.force_login(self.user1)
        url = reverse('notes:delete', kwargs={'slug': self.note2.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_duplicate_slug_creation(self):
        """
        Проверка что невозможно создать две заметки с одинаковым slug.
        """
        duplicate_note_data = {
            'title': 'Duplicate Note',
            'text': 'This is a duplicate note',
            'slug': '1',
        }
        self.client.force_login(self.user1)
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

from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


class NotesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Создаем клиенты для тестирования
        """
        super().setUpClass()
        cls.client = Client()

    def setUp(self):
        """
        Создаем пользователей и заметки для тестов
        """
        self.user1 = User.objects.create_user(
            username='user1',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password2'
        )
        self.note1 = Note.objects.create(
            title='Заметка 1',
            text='Текст заметки 1',
            author=self.user1
        )
        self.note2 = Note.objects.create(
            title='Заметка 2',
            text='Текст заметки 2',
            author=self.user2
        )
        self.client.force_login(self.user1)

    def test_note_list_view(self):
        """
        Тестирование просмотра списка заметок
        """
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.note1, response.context['object_list'])

    def test_note_create_form(self):
        """
        Тестирование формы создания заметки
        """
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_update_form(self):
        """
        Тестирование формы обновления заметки
        """
        response = self.client.get(
            reverse('notes:edit', kwargs={'slug': self.note1.slug})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response.context['form'], NoteForm)
        self.assertEqual(response.context['form'].instance, self.note1)

    def test_notes_list_only_contains_user_notes(self):
        """
        Тестирование списка заметок, содержащего только заметки пользователя
        """
        url = reverse('notes:list')
        self.client.force_login(self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        notes = response.context['object_list']
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0], self.note2)

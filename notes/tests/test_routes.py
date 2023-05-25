from http import HTTPStatus

from django.contrib.auth.models import User
from django.shortcuts import resolve_url
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


class HomeTestCase(TestCase):
    def test_home_page_accessible(self):
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class NoteTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')

    def test_notes_list_access(self):
        response = self.client.get('/notes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'notes/list.html')

    def test_note_create_access(self):
        response = self.client.get('/add/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'notes/form.html')

    def test_note_success_access(self):
        response = self.client.get('/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'notes/success.html')


class NotePageAccessTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='author', password='password'
        )
        self.other_user = User.objects.create_user(
            username='other_user', password='password'
        )
        self.note = Note.objects.create(
            author=self.author, title='Заголовок', text='Текст заметки'
        )

    def test_note_detail_access(self):
        # Автор заметки должен иметь доступ к странице с подробной информацией о заметке
        self.client.login(username='author', password='password')
        url = reverse('notes:detail', kwargs={'slug': self.note.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Другой пользователь не должен иметь доступ к странице с подробной информацией о заметке
        self.client.login(username='other_user', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_note_edit_access(self):
        # Автор заметки должен иметь доступ к странице редактирования заметки
        self.client.login(username='author', password='password')
        url = reverse('notes:edit', kwargs={'slug': self.note.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Другой пользователь не должен иметь доступ к странице редактирования заметки
        self.client.login(username='other_user', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_note_delete_access(self):
        # Автор заметки должен иметь доступ к странице удаления заметки
        self.client.login(username='author', password='password')
        url = reverse('notes:delete', kwargs={'slug': self.note.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Другой пользователь не должен иметь доступ к странице удаления заметки
        self.client.login(username='other_user', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class NoteListPageAccessTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

        self.note = Note.objects.create(
            title='Test Note', text='This is a test note', author=self.user
        )

    def test_anonymous_user_redirect_to_login_on_notes_list(self):
        # Анонимный пользователь пытается получить доступ к странице списка заметок
        response = self.client.get(reverse('notes:list'))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            resolve_url('/auth/login/') + '?next=' + reverse('notes:list'),
        )

    def test_anonymous_user_redirect_to_login_on_note_success(self):
        # Анонимный пользователь пытается получить доступ к странице успешного добавления заметки
        response = self.client.get(reverse('notes:success'))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            resolve_url('/auth/login/') + '?next=' + reverse('notes:success'),
        )

    def test_anonymous_user_redirect_to_login_on_note_create(self):
        # Анонимный пользователь пытается получить доступ к странице создания заметки
        response = self.client.get(reverse('notes:add'))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            resolve_url('/auth/login/') + '?next=' + reverse('notes:add'),
        )

    def test_anonymous_user_redirect_to_login_on_note_detail(self):
        # Анонимный пользователь пытается получить доступ к странице отдельной заметки
        response = self.client.get(
            reverse('notes:detail', args=[self.note.slug])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            resolve_url('/auth/login/')
            + '?next='
            + reverse('notes:detail', args=[self.note.slug]),
        )

    def test_anonymous_user_redirect_to_login_on_note_update(self):
        # Анонимный пользователь пытается получить доступ к странице редактирования заметки
        response = self.client.get(
            reverse('notes:edit', args=[self.note.slug])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            resolve_url('/auth/login/')
            + '?next='
            + reverse('notes:edit', args=[self.note.slug]),
        )

    def test_anonymous_user_redirect_to_login_on_note_delete(self):
        # Анонимный пользователь пытается получить доступ к странице удаления заметки
        response = self.client.get(
            reverse('notes:delete', args=[self.note.slug])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            resolve_url('/auth/login/')
            + '?next='
            + reverse('notes:delete', args=[self.note.slug]),
        )


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

    def test_login_page(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_logout_user(self):
        # Проверка выхода из учетной записи
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup_page(self):
        # Проверка доступности страницы регистрации
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'registration/signup.html')

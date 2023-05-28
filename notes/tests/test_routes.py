from http import HTTPStatus

from django.contrib.auth.models import User
from django.shortcuts import resolve_url, reverse
from django.test import TestCase

from notes.models import Note


class NoteAppTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.author = User.objects.create_user(
            username='author', password='password'
        )
        self.other_user = User.objects.create_user(
            username='other_user', password='password'
        )
        self.note = Note.objects.create(
            author=self.author, title='Заголовок', text='Текст заметки'
        )

    def test_home_page_accessible(self):
        # Проверка доступности домашней страницы
        test_cases = [
            ('notes:home', 'notes/home.html'),
        ]
        for url_name, template_name in test_cases:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template_name)

    def test_pages_accessibility(self):
        # Проверка доступности страниц Аутентифицированному пользователю
        self.client.force_login(self.user)
        test_cases = [
            ('notes:list', 'notes/list.html'),
            ('notes:success', 'notes/success.html'),
            ('notes:add', 'notes/form.html'),
        ]
        for url_name, template_name in test_cases:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template_name)

    def test_authorized_user_access(self):
        # проверка доступа cтраницы отдельной заметки,
        # удаления и редактирования заметки
        # для авторизированного пользователя
        test_cases = [
            ('detail', HTTPStatus.OK),
            ('edit', HTTPStatus.OK),
            ('delete', HTTPStatus.OK),
        ]

        for view_name, allowed_status in test_cases:
            with self.subTest(view_name=view_name):
                self.client.force_login(self.author)
                url = reverse(
                    f'notes:{view_name}', kwargs={'slug': self.note.slug}
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, allowed_status)

    def test_unauthorized_user_access(self):
        # проверка доступа cтраницы отдельной заметки,
        # удаления и редактирования заметки
        # для не авторизированного пользователя
        test_cases = [
            ('detail', HTTPStatus.NOT_FOUND),
            ('edit', HTTPStatus.NOT_FOUND),
            ('delete', HTTPStatus.NOT_FOUND),
        ]

        for view_name, forbidden_status in test_cases:
            with self.subTest(view_name=view_name):
                self.client.force_login(self.other_user)
                url = reverse(
                    f'notes:{view_name}', kwargs={'slug': self.note.slug}
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, forbidden_status)

    def test_anonymous_user_redirect_to_login(self):
        url_mappings = [
            ('notes:list', []),
            ('notes:success', []),
            ('notes:add', []),
            ('notes:detail', [self.note.slug]),
            ('notes:edit', [self.note.slug]),
            ('notes:delete', [self.note.slug]),
        ]
        for url_name, args in url_mappings:
            with self.subTest(url_name=url_name):
                if args:
                    url = reverse(url_name, args=args)
                else:
                    url = reverse(url_name)
                response = self.client.get(url)
                expected_redirect_url = (
                    resolve_url('/auth/login/') + '?next=' + url
                )
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, expected_redirect_url)

    def test_pages(self):
        # проверка Страницы регистрации пользователей,
        # входа в учётную запись и выхода из неё доступны всем пользователям
        page_templates = [
            ('users:login', 'registration/login.html'),
            ('users:logout', 'registration/logout.html'),
            ('users:signup', 'registration/signup.html'),
        ]

        for url_name, template_name in page_templates:
            with self.subTest(url=url_name, template=template_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template_name)

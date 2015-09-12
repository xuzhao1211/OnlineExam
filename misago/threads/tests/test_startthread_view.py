# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.conf import settings
from django.core.urlresolvers import reverse

from misago.acl.testutils import override_acl
from misago.forums.models import Forum
from misago.users.testutils import AuthenticatedUserTestCase

from misago.threads.models import Label, Thread


class StartThreadTests(AuthenticatedUserTestCase):
    ajax_header = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

    def setUp(self):
        super(StartThreadTests, self).setUp()

        self.forum = Forum.objects.all_forums().filter(role="forum")[:1][0]
        self.link = reverse('misago:start_thread', kwargs={
            'forum_id': self.forum.id
        })

        Label.objects.clear_cache()

    def tearDown(self):
        Label.objects.clear_cache()

    def allow_start_thread(self, extra_acl=None):
        forums_acl = self.user.acl
        forums_acl['visible_forums'].append(self.forum.pk)
        forums_acl['forums'][self.forum.pk] = {
            'can_see': 1,
            'can_browse': 1,
            'can_start_threads': 1,
        }

        if extra_acl:
            forums_acl['forums'][self.forum.pk].update(extra_acl)
        override_acl(self.user, forums_acl)

    def test_cant_see(self):
        """has no permission to see forum"""
        forums_acl = self.user.acl
        forums_acl['visible_forums'].remove(self.forum.pk)
        forums_acl['forums'][self.forum.pk] = {
            'can_see': 0,
            'can_browse': 0,
            'can_start_threads': 1,
        }
        override_acl(self.user, forums_acl)

        response = self.client.get(self.link, **self.ajax_header)
        self.assertEqual(response.status_code, 404)

    def test_cant_browse(self):
        """has no permission to browse forum"""
        forums_acl = self.user.acl
        forums_acl['visible_forums'].append(self.forum.pk)
        forums_acl['forums'][self.forum.pk] = {
            'can_see': 1,
            'can_browse': 0,
            'can_start_threads': 1,
        }
        override_acl(self.user, forums_acl)

        response = self.client.get(self.link, **self.ajax_header)
        self.assertEqual(response.status_code, 403)

    def test_cant_start_thread_in_locked_forum(self):
        """can't post in closed forum"""
        self.forum.is_closed = True
        self.forum.save()

        forums_acl = self.user.acl
        forums_acl['visible_forums'].append(self.forum.pk)
        forums_acl['forums'][self.forum.pk] = {
            'can_see': 1,
            'can_browse': 1,
            'can_start_threads': 1,
        }
        override_acl(self.user, forums_acl)

        response = self.client.get(self.link, **self.ajax_header)
        self.assertEqual(response.status_code, 403)

    def test_cant_start_thread_as_guest(self):
        """guests can't start threads"""
        self.client.post(reverse(settings.LOGOUT_URL))

        response = self.client.get(self.link, **self.ajax_header)
        self.assertEqual(response.status_code, 403)

    def test_empty_start_thread_form(self):
        """empty new thread form has no crashes"""
        self.allow_start_thread({
            'can_pin_threads': 1,
            'can_close_threads': 1,
        })

        response = self.client.post(self.link, data={
            'submit': True,
        },
        **self.ajax_header)
        self.assertEqual(response.status_code, 200)

    def test_can_start_thread(self):
        """can post new thread"""
        self.allow_start_thread()
        response = self.client.get(self.link, **self.ajax_header)
        self.assertEqual(response.status_code, 200)

        self.allow_start_thread()
        response = self.client.post(self.link, data={
            'title': 'Hello, I am test thread!',
            'post': 'Lorem ipsum dolor met!',
            'submit': True,
        },
        **self.ajax_header)
        self.assertEqual(response.status_code, 200)

        last_thread = self.user.thread_set.all()[:1][0]

        response_dict = json.loads(response.content)
        self.assertIn('post_url', response_dict)

        self.allow_start_thread()
        response = self.client.get(response_dict['post_url'])
        self.assertEqual(response.status_code, 200)
        self.assertIn(last_thread.title, response.content)

        updated_user = self.user.lock()
        self.assertEqual(updated_user.threads, 1)
        self.assertEqual(updated_user.posts, 1)

        self.assertEqual(last_thread.forum_id, self.forum.pk)
        self.assertEqual(last_thread.title, "Hello, I am test thread!")
        self.assertEqual(last_thread.starter_id, updated_user.id)
        self.assertEqual(last_thread.starter_name, updated_user.username)
        self.assertEqual(last_thread.starter_slug, updated_user.slug)
        self.assertEqual(last_thread.last_poster_id, updated_user.id)
        self.assertEqual(last_thread.last_poster_name, updated_user.username)
        self.assertEqual(last_thread.last_poster_slug, updated_user.slug)

        last_post = self.user.post_set.all()[:1][0]
        self.assertEqual(last_post.forum_id, self.forum.pk)
        self.assertEqual(last_post.original, 'Lorem ipsum dolor met!')
        self.assertEqual(last_post.poster_id, updated_user.id)
        self.assertEqual(last_post.poster_name, updated_user.username)

        updated_forum = Forum.objects.get(id=self.forum.id)
        self.assertEqual(updated_forum.threads, 1)
        self.assertEqual(updated_forum.posts, 1)
        self.assertEqual(updated_forum.last_thread_id, last_thread.id)
        self.assertEqual(updated_forum.last_thread_title, last_thread.title)
        self.assertEqual(updated_forum.last_thread_slug, last_thread.slug)

        self.assertEqual(updated_forum.last_poster_id, updated_user.id)
        self.assertEqual(updated_forum.last_poster_name,
                         updated_user.username)
        self.assertEqual(updated_forum.last_poster_slug, updated_user.slug)

    def test_start_closed_thread(self):
        """can post closed thread"""
        prefix = 'misago.threads.posting.threadclose.ThreadCloseFormMiddleware'
        field_name = '%s-is_closed' % prefix

        self.allow_start_thread({'can_close_threads': 1})
        response = self.client.get(self.link, **self.ajax_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn(field_name, response.content)

        self.allow_start_thread({'can_close_threads': 1})
        response = self.client.post(self.link, data={
            'title': 'Hello, I am test thread!',
            'post': 'Lorem ipsum dolor met!',
            field_name: 1,
            'submit': True,
        },
        **self.ajax_header)
        self.assertEqual(response.status_code, 200)

        last_thread = self.user.thread_set.all()[:1][0]
        self.assertTrue(last_thread.is_closed)

    def test_start_pinned_thread(self):
        """can post pinned thread"""
        prefix = 'misago.threads.posting.threadpin.ThreadPinFormMiddleware'
        field_name = '%s-is_pinned' % prefix

        self.allow_start_thread({'can_pin_threads': 1})
        response = self.client.get(self.link, **self.ajax_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn(field_name, response.content)

        self.allow_start_thread({'can_pin_threads': 1})
        response = self.client.post(self.link, data={
            'title': 'Hello, I am test thread!',
            'post': 'Lorem ipsum dolor met!',
            field_name: 1,
            'submit': True,
        },
        **self.ajax_header)
        self.assertEqual(response.status_code, 200)

        last_thread = self.user.thread_set.all()[:1][0]
        self.assertTrue(last_thread.is_pinned)

    def test_start_labeled_thread(self):
        """can post labeled thread"""
        prefix = 'misago.threads.posting.threadlabel.ThreadLabelFormMiddleware'
        field_name = '%s-label' % prefix

        label = Label.objects.create(name="Label", slug="label")
        label.forums.add(self.forum)

        self.allow_start_thread({'can_change_threads_labels': 1})
        response = self.client.get(self.link, **self.ajax_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn(field_name, response.content)

        self.allow_start_thread({'can_change_threads_labels': 1})
        response = self.client.post(self.link, data={
            'title': 'Hello, I am test thread!',
            'post': 'Lorem ipsum dolor met!',
            field_name: label.pk,
            'submit': True,
        },
        **self.ajax_header)
        self.assertEqual(response.status_code, 200)

        last_thread = self.user.thread_set.all()[:1][0]
        self.assertEqual(last_thread.label_id, label.id)

    def test_unicode(self):
        """unicode chars can be posted"""
        self.allow_start_thread()
        response = self.client.post(self.link, data={
            'title': 'Brzęczyżczykiewicz',
            'post': 'Chrzążczyżewoszyce, powiat Łękółody.',
            'preview': True},
        **self.ajax_header)
        self.assertEqual(response.status_code, 200)

    def test_empty_form(self):
        """empty form has no errors"""
        self.allow_start_thread()
        response = self.client.post(self.link, data={
            'title': '',
            'post': '',
            'preview': True},
        **self.ajax_header)
        self.assertEqual(response.status_code, 200)

        self.allow_start_thread()
        response = self.client.post(self.link, data={
            'title': '',
            'post': '',
            'submit': True},
        **self.ajax_header)
        self.assertEqual(response.status_code, 200)

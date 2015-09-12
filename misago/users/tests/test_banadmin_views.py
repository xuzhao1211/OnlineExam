from datetime import date, datetime, timedelta

from django.core.urlresolvers import reverse

from misago.admin.testutils import AdminTestCase

from misago.users.models import Ban


class BanAdminViewsTests(AdminTestCase):
    def test_link_registered(self):
        """admin nav contains bans link"""
        response = self.client.get(
            reverse('misago:admin:users:accounts:index'))

        response = self.client.get(response['location'])
        self.assertIn(reverse('misago:admin:users:bans:index'),
                      response.content)

    def test_list_view(self):
        """bans list view returns 200"""
        response = self.client.get(reverse('misago:admin:users:bans:index'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(response['location'])
        self.assertEqual(response.status_code, 200)

    def test_mass_delete(self):
        """adminview deletes multiple bans"""
        test_date = datetime.now() + timedelta(days=180)

        for i in xrange(10):
            response = self.client.post(
                reverse('misago:admin:users:bans:new'),
                data={
                    'check_type': '1',
                    'banned_value': '%stest@test.com' % i,
                    'user_message': 'Lorem ipsum dolor met',
                    'staff_message': 'Sit amet elit',
                    'expires_on': test_date.isoformat(),
                })
            self.assertEqual(response.status_code, 302)

        self.assertEqual(Ban.objects.count(), 10)

        bans_pks = []
        for ban in Ban.objects.iterator():
            bans_pks.append(ban.pk)

        response = self.client.post(
            reverse('misago:admin:users:bans:index'),
            data={'action': 'delete', 'selected_items': bans_pks})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ban.objects.count(), 0)

    def test_new_view(self):
        """new ban view has no showstoppers"""
        response = self.client.get(
            reverse('misago:admin:users:bans:new'))
        self.assertEqual(response.status_code, 200)

        test_date = datetime.now() + timedelta(days=180)

        response = self.client.post(
            reverse('misago:admin:users:bans:new'),
            data={
                'check_type': '1',
                'banned_value': 'test@test.com',
                'user_message': 'Lorem ipsum dolor met',
                'staff_message': 'Sit amet elit',
                'expires_on': test_date.isoformat(),
            })
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('misago:admin:users:bans:index'))
        response = self.client.get(response['location'])
        self.assertEqual(response.status_code, 200)
        self.assertIn('test@test.com', response.content)

    def test_edit_view(self):
        """edit ban view has no showstoppers"""
        self.client.post(
            reverse('misago:admin:users:bans:new'),
            data={
                'check_type': '0',
                'banned_value': 'Admin',
            })

        test_ban = Ban.objects.get(banned_value='admin')
        response = self.client.post(
            reverse('misago:admin:users:bans:edit',
                    kwargs={'ban_id': test_ban.pk}),
            data={
                'check_type': '1',
                'banned_value': 'test@test.com',
                'user_message': 'Lorem ipsum dolor met',
                'staff_message': 'Sit amet elit',
                'expires_on': '',
            })
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('misago:admin:users:bans:index'))
        response = self.client.get(response['location'])
        self.assertEqual(response.status_code, 200)
        self.assertIn('test@test.com', response.content)

    def test_delete_view(self):
        """delete ban view has no showstoppers"""
        self.client.post(
            reverse('misago:admin:users:bans:new'),
            data={
                'check_type': '0',
                'banned_value': 'TestBan',
            })

        test_ban = Ban.objects.get(banned_value='testban')

        response = self.client.post(
            reverse('misago:admin:users:bans:delete',
                    kwargs={'ban_id': test_ban.pk}))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('misago:admin:users:bans:index'))
        self.client.get(response['location'])
        response = self.client.get(response['location'])

        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_ban.banned_value not in response.content)

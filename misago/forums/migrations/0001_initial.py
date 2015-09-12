# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('misago_acl', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('special_role', models.CharField(max_length=255, null=True, blank=True)),
                ('role', models.CharField(max_length=255, null=True, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('is_closed', models.BooleanField(default=False)),
                ('redirect_url', models.CharField(max_length=255, null=True, blank=True)),
                ('redirects', models.PositiveIntegerField(default=0)),
                ('threads', models.PositiveIntegerField(default=0)),
                ('posts', models.PositiveIntegerField(default=0)),
                ('last_thread_title', models.CharField(max_length=255, null=True, blank=True)),
                ('last_thread_slug', models.CharField(max_length=255, null=True, blank=True)),
                ('last_poster_name', models.CharField(max_length=255, null=True, blank=True)),
                ('last_poster_slug', models.CharField(max_length=255, null=True, blank=True)),
                ('last_post_on', models.DateTimeField(null=True, blank=True)),
                ('prune_started_after', models.PositiveIntegerField(default=0)),
                ('prune_replied_after', models.PositiveIntegerField(default=0)),
                ('css_class', models.CharField(max_length=255, null=True, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('archive_pruned_in', models.ForeignKey(related_name='pruned_archive', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='misago_forums.Forum', null=True)),
                ('last_poster', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='misago_forums.Forum', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ForumRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('special_role', models.CharField(max_length=255, null=True, blank=True)),
                ('pickled_permissions', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoleForumACL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('forum', models.ForeignKey(related_name='forum_role_set', to='misago_forums.Forum')),
                ('forum_role', models.ForeignKey(to='misago_forums.ForumRole', to_field='id')),
                ('role', models.ForeignKey(related_name='forums_acls', to='misago_acl.Role')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

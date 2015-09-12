from django.db.transaction import atomic
from django.utils import timezone

from misago.notifications import read_user_notifications

from misago.readtracker import forumstracker, signals
from misago.readtracker.dates import is_date_tracked
from misago.readtracker.models import ForumRead, ThreadRead


__all__ = ['make_read_aware', 'read_thread']


def make_read_aware(user, target):
    if hasattr(target, '__iter__'):
        make_threads_read_aware(user, target)
    else:
        make_thread_read_aware(user, target)


def make_threads_read_aware(user, threads, forum=None):
    if not threads:
        return None

    if user.is_anonymous():
        make_read(threads)
        return None

    if forum:
        make_forum_threads_read_aware(user, forum, threads)
    else:
        make_forums_threads_read_aware(user, threads)


def make_read(threads):
    for thread in threads:
        thread.unread_replies = 0
        thread.is_read = True
        thread.is_new = False


def make_forum_threads_read_aware(user, forum, threads):
    if forum.is_read:
        make_read(threads)
    else:
        threads_dict = {}
        for thread in threads:
            thread.is_read = not is_date_tracked(
                thread.last_post_on, user, forum.last_read_on)
            thread.is_new = True
            if thread.is_read:
                thread.unread_replies = 0
            else:
                thread.unread_replies = thread.replies
                threads_dict[thread.pk] = thread

        if threads_dict:
            make_threads_dict_read_aware(user, threads_dict)


def make_forums_threads_read_aware(user, threads):
    forums_cutoffs = fetch_forums_cutoffs_for_threads(user, threads)

    threads_dict = {}
    for thread in threads:
        thread.is_read = not is_date_tracked(
            thread.last_post_on, user, forums_cutoffs.get(thread.forum_id))
        thread.is_new = True
        if thread.is_read:
            thread.unread_replies = 0
        else:
            thread.unread_replies = thread.replies
            threads_dict[thread.pk] = thread

    if threads_dict:
        make_threads_dict_read_aware(user, threads_dict)


def fetch_forums_cutoffs_for_threads(user, threads):
    forums = []
    for thread in threads:
        if thread.forum_id not in forums:
            forums.append(thread.forum_id)

    forums_dict = {}
    for record in user.forumread_set.filter(forum__in=forums):
        forums_dict[record.forum_id] = record.last_read_on
    return forums_dict


def make_threads_dict_read_aware(user, threads_dict):
    for record in user.threadread_set.filter(thread__in=threads_dict.keys()):
        if record.thread_id in threads_dict:
            thread = threads_dict[record.thread_id]
            thread.is_new = False
            thread.is_read = record.last_read_on >= thread.last_post_on
            if thread.is_read:
                thread.unread_replies = 0
            else:
                thread.unread_replies = thread.replies - record.read_replies
                if thread.unread_replies < 1:
                    thread.unread_replies = 1


def make_thread_read_aware(user, thread):
    thread.is_read = True
    thread.is_new = False
    thread.read_record = None

    if user.is_anonymous():
        thread.last_read_on = timezone.now()
    else:
        thread.last_read_on = user.reads_cutoff

    if user.is_authenticated() and is_date_tracked(thread.last_post_on, user):
        thread.is_read = False
        thread.is_new = True

        try:
            forum_record = user.forumread_set.get(forum_id=thread.forum_id)
            if thread.last_post_on > forum_record.last_read_on:
                try:
                    thread_record = user.threadread_set.get(thread=thread)
                    thread.last_read_on = thread_record.last_read_on
                    thread.is_new = False
                    if thread.last_post_on <= thread_record.last_read_on:
                        thread.is_read = True
                    thread.read_record = thread_record
                except ThreadRead.DoesNotExist:
                    pass
            else:
                thread.is_read = True
                thread.is_new = False
        except ForumRead.DoesNotExist:
            forumstracker.start_record(user, thread.forum)


def make_posts_read_aware(user, thread, posts):
    try:
        is_thread_read = thread.is_read
    except AttributeError:
        raise ValueError("thread passed make_posts_read_aware should be "
                         "read aware too via make_thread_read_aware")

    if is_thread_read:
        for post in posts:
            post.is_read = True
    else:
        for post in posts:
            if is_date_tracked(post.posted_on, user):
                post.is_read = post.posted_on <= thread.last_read_on
            else:
                post.is_read = True


def read_thread(user, thread, last_read_reply):
    if not thread.is_read:
        if thread.last_read_on < last_read_reply.posted_on:
            sync_record(user, thread, last_read_reply)


@atomic
def sync_record(user, thread, last_read_reply):
    notification_triggers = ['read_thread_%s' % thread.pk]

    read_replies = count_read_replies(user, thread, last_read_reply)
    if thread.read_record:
        thread.read_record.read_replies = read_replies
        thread.read_record.last_read_on = last_read_reply.posted_on
        thread.read_record.save(update_fields=['read_replies', 'last_read_on'])
    else:
        user.threadread_set.create(
            forum=thread.forum,
            thread=thread,
            read_replies=read_replies,
            last_read_on=last_read_reply.posted_on)
        signals.thread_tracked.send(sender=user, thread=thread)
        notification_triggers.append('see_thread_%s' % thread.pk)

    if last_read_reply.posted_on == thread.last_post_on:
        signals.thread_read.send(sender=user, thread=thread)
        forumstracker.sync_record(user, thread.forum)

    read_user_notifications(user, notification_triggers, False)


def count_read_replies(user, thread, last_read_reply):
    last_reply_date = last_read_reply.posted_on
    queryset = thread.post_set.filter(posted_on__lte=last_reply_date)
    queryset = queryset.filter(is_moderated=False)
    return queryset.count() - 1 # - starters post

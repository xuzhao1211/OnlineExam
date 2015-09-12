from datetime import timedelta

from django.conf import settings
from django.utils import timezone


def is_date_tracked(date, user, forum_read_cutoff=None):
    if date:
        if forum_read_cutoff and forum_read_cutoff > date:
            return False
        else:
            return date > user.reads_cutoff
    else:
        return False

from django.db import models

from misago.core.cache import cache
from misago.core.utils import slugify


CACHE_NAME = 'misago_threads_labels'


class LabelManager(models.Manager):
    def get_forum_labels(self, forum):
        labels = []
        for label in self.get_cached_labels():
            if forum.pk in label.forums_ids:
                labels.append(label)
        return labels

    def get_cached_labels_dict(self):
        return dict([(label.pk, label) for label in self.get_cached_labels()])

    def get_cached_labels(self):
        labels = cache.get(CACHE_NAME, 'nada')
        if labels == 'nada':
            labels = []
            labels_qs = self.all().prefetch_related('forums')
            for label in labels_qs.order_by('name'):
                label.forums_ids = [f.pk for f in label.forums.all()]
                labels.append(label)
            cache.set(CACHE_NAME, labels)
        return labels

    def clear_cache(self):
        cache.delete(CACHE_NAME)


class Label(models.Model):
    forums = models.ManyToManyField('misago_forums.Forum')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    css_class = models.CharField(max_length=255, null=True, blank=True)

    objects = LabelManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            self.strip_inavailable_labels()
        Label.objects.clear_cache()
        return super(Label, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        Label.objects.clear_cache()
        return super(Label, self).delete(*args, **kwargs)

    def strip_inavailable_labels(self):
        qs = self.thread_set
        if self.forums:
            qs = qs.exclude(forum__in=self.forums.all())
        qs.update(label=None)

    def set_name(self, name):
        self.name = name
        self.slug = slugify(name)

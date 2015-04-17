from __future__ import absolute_import

from django.forms.models import model_to_dict

from uuid import uuid4

import gc


def new_uuid4_hex():
    return uuid4().hex


def chunked(queryset, chunksize=100):
    '''''
    https://djangosnippets.org/snippets/1949/

    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 100) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    #pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    pk = last_pk
    queryset = queryset.order_by('-pk')
    while pk >= 0:
        for row in queryset.filter(pk__lte=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


def sql_regex(column, type='regex'):
    '''See:

    http://stackoverflow.com/questions/10653162/django-search-a-list-of-regexp-stored-in-a-model

    For more info.
    '''
    from django.db import backend
    op = backend.DatabaseWrapper.operators[type].replace(
        '%s', column)
    return '%s ' + op


class ModelDiffMixin(object):
    """
    See: http://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed

    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.

    Usage:
    >>> p = Place()
    >>> p.has_changed
    False
    >>> p.changed_fields
    []
    >>> p.rank = 42
    >>> p.has_changed
    True
    >>> p.changed_fields
    ['rank']
    >>> p.diff
    {'rank': (0, 42)}
    >>> p.categories = [1, 3, 5]
    >>> p.diff
    {'categories': (None, [1, 3, 5]), 'rank': (0, 42)}
    >>> p.get_field_diff('categories')
    (None, [1, 3, 5])
    >>> p.get_field_diff('rank')
    (0, 42)

    """

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

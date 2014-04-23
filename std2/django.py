from __future__ import absolute_import


def sql_regex(column, type='regex'):
    '''See:

    http://stackoverflow.com/questions/10653162/django-search-a-list-of-regexp-stored-in-a-model

    For more info.
    '''
    from django.db import backend
    op = backend.DatabaseWrapper.operators[type].replace(
        '%s', column)
    return '%s ' + op
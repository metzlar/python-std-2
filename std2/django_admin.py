from __future__ import absolute_import

from django.contrib import admin
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse_lazy as reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


def get_admin_for(model_type):
    '''
    Retrieve a ModelAdmin instance for the given
    `model_type` class.
    '''

    return admin.site._registry[model_type]


def invoke_action(
        modeladmin_instance,
        action,
        queryset,
        request = None,
        request_uri = None
):
    '''
    Invoke a ModelAdmin action withouth a (real) request.

    This is useful to invoke some action from e.g. a management command.

    Arguments:
     - modeladmin_instance The ModelAdmin that holds the actions.
     - action The name (str) of the action.
     - queryset A queryset to perform the action on.
     - request Optional request, if not set it defaults to a POST to
       the model's changelist with data
       `{_selected_action:[queryset],action:"action",post:"post"}`
     - request_uri An optional string that will assume the default request (`request = None`)
       but use the provided url instead of the standard model's changelist.

    Warning: If no request is supplied the first *active superuser* in the database is used
    as the executing user (tied to `request.user`) this is potentially unsafe.

    Example usage:

    u = User.objects.filter(username='john')
    model_admin = get_admin_for(u[0])
    invoke_action(model_admin, 'delete', u)
    '''

    if request is None:
        
        if request_uri is None:
            ct = ContentType.objects.get_for_model(modeladmin_instance.model)
            request_uri = reverse(
                'admin:{app_label}_{model_name}_changelist'.format(
                    app_label = ct.app_label,
                    model_name = ct.model,
                )
            )
            
        rf = RequestFactory()
        
        request = rf.post(
            request_uri,
            {
                '_selected_action': queryset,
                'action': action,
                'post': 'post',
            }
        )
        request.user = User.objects.filter(is_superuser=True, is_active=True)[0]

    (action_method, action_name, action_description) = modeladmin_instance.get_action(action)
    return action_method(modeladmin_instance, request, queryset)

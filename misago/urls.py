from django.conf import settings
from django.conf.urls import patterns, include, url


urlpatterns = patterns('misago.core.views',
    # "misago:index" link symbolises "root" of Misago links space
    # any request with path that falls below this one is assumed to be directed
    # at Misago and will be handled by misago.views.exceptionhandler if it
    # results in Http404 or PermissionDenied exception
    url(r'^$', 'forum_index', name='index'),
)

# Register Misago Apps
urlpatterns += patterns('',
    url(r'^', include('misago.legal.urls')),
    url(r'^', include('misago.users.urls')),
    url(r'^', include('misago.notifications.urls')),
    url(r'^', include('misago.forums.urls')),
    url(r'^', include('misago.threads.urls')),
    url(r'^', include('misago.readtracker.urls')),
    # UI Server view that handles realtime updates of Misago UI
    url(r'^ui-server/$', 'misago.core.uiviews.uiserver', name="ui_server"),
)

# Register API
apipatterns = patterns('',
    url(r'^legal-pages/', include('misago.legal.urls.api')),
    url(r'^', include('misago.users.urls.api')),
)

urlpatterns += patterns('',
    url(r'^api/', include(apipatterns, namespace='api')),
)


# Register Misago ACP
if settings.MISAGO_ADMIN_PATH:
    # Admin patterns recognised by Misago
    adminpatterns = patterns('',
        url(r'^', include('misago.admin.urls')),
    )

    admin_prefix = r'^%s/' % settings.MISAGO_ADMIN_PATH
    urlpatterns += patterns('',
        url(admin_prefix, include(adminpatterns, namespace='admin')),
    )


# Make error pages accessible casually in DEBUG
if settings.DEBUG:
    urlpatterns += patterns('misago.core.errorpages',
        url(r'^403/$', 'permission_denied'),
        url(r'^404/$', 'page_not_found'),
        url(r'^405/$', 'not_allowed'),
        url(r'^csrf-failure/$', 'csrf_failure'),
    )

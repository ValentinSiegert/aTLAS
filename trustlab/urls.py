import os
from django.urls import re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles import views
from .views.index_view import IndexView
from .views.api.scenarios_api import ScenariosAPI
from .consumers.lab_consumer import LabConsumer
from .consumers.supervisors_consumer import SupervisorsConsumer
from django.views.defaults import page_not_found

urlpatterns = [
    re_path(r'^$', IndexView.as_view(), name='index'),
    re_path(r'^lab/$', page_not_found, {'exception': Exception('Not Found')}, name="lab"),
    re_path(r'^supervisors/$', page_not_found, {'exception': Exception('Not Found')}, name="supervisors"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
API URLs
"""
urlpatterns += [
    re_path(r'^api/scenarios', ScenariosAPI.as_view(), name="scenario"),
]

"""
Debug URLs
"""
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', views.serve, {'document_root': os.path.join(settings.BASE_DIR, 'trustlab\static')}),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


"""
WS Routing
"""
websocket_urlpatterns = [
    re_path(r'^supervisors/$', SupervisorsConsumer),
    re_path(r'^lab/$', LabConsumer),
]

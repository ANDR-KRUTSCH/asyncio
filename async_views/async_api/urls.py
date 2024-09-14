from django.urls import path
from . import views

app_name = 'async_api'

urlpatterns = (
    path(route='', view=views.requests_view, name='requests'),
    # path(route='sync_to_async', view=views.sync_to_async_view, name='sync_to_async'),
    # path(route='async_to_sync', view=views.requests_view_sync, name='async_to_sync'),
)
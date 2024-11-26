"""
URL configuration for storm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path
from api.views.data import DataAPIView
from api.views.devices import DevicesAPIView
from api.views.doors import DoorsAPIView
from api.views.room_detail import RoomDetailAPIView
from api.views.rooms import RoomsAPIView
from api.views.metrics import MetricsAPIView
from api.views.context import ContextAPIView
import django_eventstream

urlpatterns = [
    path("admin/", admin.site.urls),
]

app_name = "api"

urlpatterns += [
    path("v1/context", ContextAPIView.as_view()),
    path("v1/data", DataAPIView.as_view()),
    path("v1/devices", DevicesAPIView.as_view()),
    path("v1/doors", DoorsAPIView.as_view()),
    path("v1/room/<identifier>/", RoomDetailAPIView.as_view(), name="room"),
    path("v1/rooms", RoomsAPIView.as_view()),
    path("v1/metrics", MetricsAPIView.as_view()),
    path("v1/events/", include(django_eventstream.urls), {"channels": ["main"]}),
]

"""
URL configuration for storm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path
from api.views import RoomDetailAPIView, RoomsAPIView
from api.views import DevicesAPIView, DoorsAPIView, DataAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
]

app_name = "api"

urlpatterns += [
    path("v1/devices", DevicesAPIView.as_view()),
    path("v1/doors", DoorsAPIView.as_view()),
    path("v1/room/<identifier>/", RoomDetailAPIView.as_view()),
    path("v1/rooms", RoomsAPIView.as_view()),
    path("v1/data", DataAPIView.as_view()),
]

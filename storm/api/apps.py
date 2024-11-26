"""
This module handles the initialization of the REST API and starts a thread for
automatic event and metric generation every five seconds.
"""

# django imports
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    This class specifies the configuration of storm's REST API.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

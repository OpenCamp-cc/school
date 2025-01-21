from django.http import HttpRequest

from .models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User

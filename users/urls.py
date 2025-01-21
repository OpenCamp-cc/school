from django.urls import include, path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('oauth/google', views.google_login_redirect, name='google-login-redirect'),
    path(
        'oauth/google/callback',
        views.google_login_callback,
        name='google-login-callback',
    ),
]

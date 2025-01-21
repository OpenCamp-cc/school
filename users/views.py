import json
import os

from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from integrations.google.client import GoogleAPIClient

from .forms import LoginForm, SignUpForm
from .models import ExternalProfile, User

google_client = GoogleAPIClient(
    client_id=os.environ.get('GOOGLE_CLIENT_ID', ''),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', ''),
    project_id=os.environ.get('GOOGLE_PROJECT_ID', ''),
    redirect_uri=os.environ.get('GOOGLE_REDIRECT_URI', ''),
    scopes=os.environ.get('GOOGLE_SCOPES', '').split(','),
)


def signup(request):
    if request.user.is_authenticated:
        return redirect('/')

    form = SignUpForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = User.objects.create(email=email, username=email)
        user.set_password(password)
        user.save()

        login(request, user)
        return redirect('/')

    return render(request, 'users/signup.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('/')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = User.objects.get(email=email)
        login(request, user)
        return redirect('/')

    return render(
        request,
        'users/login.html',
        {'form': form},
    )


def logout_user(request):
    logout(request)
    return redirect('/')


def google_login_redirect(request):
    """
    Starts the Google Login oauth flow.
    Google's response will be handled in the google_login_callback view.
    """
    url = google_client.get_oauth_authorization_url()
    return redirect(url)


def google_login_callback(request):
    """
    Supports both login and signup flows.
    If the user is already signed in, we will update the user's Google OAuth credentials.
    If they are not signed in, we will create the user account and sign them in.
    """
    code = request.GET.get('code')
    creds = google_client.get_oauth_credentials(code)

    oauth_profile = google_client.get_user_profile(
        token=creds['token'], refresh_token=creds['refresh_token']
    )

    email = oauth_profile['email']

    if request.user.is_authenticated:
        user = request.user
    else:
        # Check if there is an existing account for the user first. If not, we create it
        try:
            user = User.objects.select_related('external_profile').get(email=email)
        except User.DoesNotExist:
            user = User(
                username=email,
                email=email,
                first_name=oauth_profile['given_name'],
                last_name=oauth_profile['family_name'],
            )
            user.set_unusable_password()
            user.save()

    profile, created = ExternalProfile.objects.get_or_create(user=user)
    profile.google_access_token = creds['token']
    profile.google_refresh_token = creds['refresh_token']
    profile.google_scopes = creds['scopes']
    profile.google_enabled = True
    profile.save()

    login(request, user)
    return redirect('/')

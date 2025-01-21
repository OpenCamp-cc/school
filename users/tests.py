import json
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from .models import ExternalProfile, User


@pytest.mark.django_db
def test_users():
    u = User.objects.create(username='testuser', email='test@email.com')

    with pytest.raises(Exception):
        u.set_manager(u)


@pytest.mark.django_db
def test_signup(client, user1):
    template = 'users/signup.html'
    url = reverse('users:signup')
    resp = client.get(url)
    assertTemplateUsed(resp, template)

    data = {
        'email': '',
        'password': '',
        'password2': '',
    }

    resp = client.post(url, data)
    assertTemplateUsed(resp, template)
    assert len(resp.context['form'].errors['email']) == 1
    assert len(resp.context['form'].errors['password']) == 1
    assert len(resp.context['form'].errors['password2']) == 1

    data['password'] = '1234'
    data['password2'] = '12345'
    resp = client.post(url, data)
    assertTemplateUsed(resp, template)
    assert len(resp.context['form'].errors['password2']) == 1

    data['email'] = user1.email
    data['password2'] = data['password']
    resp = client.post(url, data)
    assertTemplateUsed(resp, template)
    assert len(resp.context['form'].errors['email']) == 1

    data['email'] = 'somethingnew@something.com'
    resp = client.post(url, data)
    assertRedirects(resp, '/', fetch_redirect_response=False)

    client.logout()
    client.force_login(user1)
    resp = client.get(url)
    assertRedirects(resp, '/', fetch_redirect_response=False)


@pytest.mark.django_db
def test_login(client, user1):
    template = 'users/login.html'
    url = reverse('users:login')
    resp = client.get(url)
    assertTemplateUsed(resp, template)

    data = {
        'email': '',
        'password': '',
    }

    resp = client.post(url, data)
    assertTemplateUsed(resp, template)
    assert len(resp.context['form'].errors['email']) == 1
    assert len(resp.context['form'].errors['password']) == 1

    data['email'] = 'a' + user1.email
    data['password'] = 'wrongpassword'
    resp = client.post(url, data)
    assertTemplateUsed(resp, template)
    assert len(resp.context['form'].errors['email']) == 1

    data['email'] = user1.email
    data['password'] = '1234'
    resp = client.post(url, data)
    assertRedirects(resp, '/', fetch_redirect_response=False)

    client.logout()
    client.force_login(user1)
    resp = client.get(url)
    assertRedirects(resp, '/', fetch_redirect_response=False)


@pytest.mark.django_db
def test_logout(client, user1):
    logout_url = reverse('users:logout')

    client.force_login(user1)
    resp = client.get(logout_url)
    assertRedirects(resp, '/', fetch_redirect_response=False)


@pytest.mark.django_db
@patch('users.views.GoogleAPIClient.get_oauth_authorization_url')
def test_google_login_redirect(mock_get_oauth_authorization_url, client):
    mock_get_oauth_authorization_url.return_value = '/oauth'
    url = reverse('users:google-login-redirect')
    response = client.get(url)
    assertRedirects(response, '/oauth', fetch_redirect_response=False)


@pytest.mark.django_db
@patch('users.views.GoogleAPIClient.get_oauth_credentials')
@patch('users.views.GoogleAPIClient.get_user_profile')
def test_google_login_callback(
    mock_get_user_profile, mock_get_oauth_credentials, client
):
    mock_get_oauth_credentials.return_value = {
        'token': 'fake-token',
        'refresh_token': 'fake-refresh-token',
        'scopes': json.dumps(['scope1', 'scope2']),
    }
    mock_get_user_profile.return_value = {
        'email': 'testuser@example.com',
        'given_name': 'Test',
        'family_name': 'User',
    }

    url = reverse('users:google-login-callback')
    response = client.get(url, {'code': 'fake-code'})

    assertRedirects(response, '/', fetch_redirect_response=False)
    user = User.objects.get(email='testuser@example.com')
    assert user.first_name == 'Test'
    assert user.last_name == 'User'
    profile = ExternalProfile.objects.get(user=user)
    assert profile.google_access_token == 'fake-token'
    assert profile.google_refresh_token == 'fake-refresh-token'
    assert profile.google_scopes
    google_scopes = json.loads(profile.google_scopes)
    assert 'scope1' in google_scopes
    assert 'scope2' in google_scopes
    assert profile.google_enabled

from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed

from users.models import User

from .models import LiveCohort


@pytest.mark.django_db
def test_search_classes(client):
    template = 'classes/search_classes.html'
    url = reverse('classes:search-classes')
    resp = client.get(url)
    assertTemplateUsed(resp, template)


@pytest.mark.django_db
def test_teacher_classes(client):
    # Create test users
    teacher = User.objects.create(username='testteacher', email='teacher@email.com')
    other_teacher = User.objects.create(
        username='otherteacher', email='other@email.com'
    )

    # Create test classes
    cohort1 = LiveCohort.objects.create(
        teacher=teacher, name='Class 1', max_students=10, price=50
    )
    cohort2 = LiveCohort.objects.create(
        teacher=teacher, name='Class 2', max_students=10, price=100
    )
    other_cohort = LiveCohort.objects.create(
        teacher=other_teacher, name='Other Class', max_students=10, price=100
    )

    template = 'classes/teacher_classes.html'
    url = reverse('classes:teacher-classes', kwargs={'user_id': teacher.id})

    # Test valid user
    resp = client.get(url)
    assertTemplateUsed(resp, template)
    assert resp.context['user'] == teacher

    # Test classes in context
    context_classes = resp.context['classes']
    assert len(context_classes) == 2
    assert cohort1 in context_classes
    assert cohort2 in context_classes
    assert other_cohort not in context_classes

    # Test invalid user
    invalid_url = reverse('classes:teacher-classes', kwargs={'user_id': 99999})
    resp = client.get(invalid_url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_add_live_cohort(client, user):
    url = reverse('classes:add-live-cohort')

    # Login Required
    response = client.get(url)
    assert response.status_code == 302  # Should redirect to login
    assert '/login' in response['Location']

    # Show add page for logged in users
    client.force_login(user)
    url = reverse('classes:add-live-cohort')
    response = client.get(url)
    assertTemplateUsed(response, 'classes/add_live_cohort.html')
    assert response.status_code == 200

    # Add live cohort success
    future_time = timezone.now() + timezone.timedelta(days=1)
    data = {
        'name': 'Test Cohort',
        'description': 'Test Description',
        'price': '99.99',
        'max_students': 10,
        'session_name': 'First Session',
        'session_description': 'Session Description',
        'start_time': future_time.strftime('%Y-%m-%dT%H:%M'),
        'end_time': (future_time + timezone.timedelta(hours=2)).strftime(
            '%Y-%m-%dT%H:%M'
        ),
    }

    response = client.post(url, data)
    assert response.status_code == 302

    # Verify cohort was created
    cohort = LiveCohort.objects.get(name='Test Cohort')
    assert cohort.teacher == user
    assert cohort.price == Decimal('99.99')
    assert cohort.max_students == 10

    # Verify session was created
    session = cohort.sessions.first()
    assert session is not None
    assert session.name == 'First Session'

    # Test invalid time range (end before start)
    future_time = timezone.now() + timezone.timedelta(days=1)
    data = {
        'name': 'Test Cohort',
        'description': 'Test Description',
        'price': '99.99',
        'max_students': 10,
        'session_name': 'First Session',
        'session_description': 'Session Description',
        'start_time': future_time.strftime('%Y-%m-%dT%H:%M'),
        'end_time': (future_time - timezone.timedelta(hours=2)).strftime(
            '%Y-%m-%dT%H:%M'
        ),
    }

    response = client.post(url, data)
    assert response.status_code == 200
    assert 'End time must be after start time' in str(response.content)
    assert LiveCohort.objects.count() == 1

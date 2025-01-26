from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed

from users.models import User

from .models import LiveCohort, LiveCohortAssignment


@pytest.mark.django_db
def test_search_classes(client):
    template = 'classes/search_classes.html'
    url = reverse('classes:search-classes')
    resp = client.get(url)
    assertTemplateUsed(resp, template)


@pytest.mark.django_db
def test_add_live_cohort(client, teacher):
    url = reverse('classes:add-live-cohort')

    # Login Required
    response = client.get(url)
    assert response.status_code == 302  # Should redirect to login
    assert '/login' in response['Location']

    # Show add page for logged in users
    client.force_login(teacher)
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
    assert cohort.teacher == teacher
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


@pytest.mark.django_db
def test_teacher_dashboard(client, user):
    url = reverse('classes:teacher-dashboard')

    # Login & Staff Required
    response = client.get(url)
    assert response.status_code == 302  # Should redirect to login
    assert '/login' in response['Location']

    # Regular user cannot access teacher dashboard
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302  # Should redirect to login

    # Staff user can access dashboard
    user.is_staff = True
    user.save()
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'classes/teacher-dashboard.html')

    # Verify dashboard shows teacher's cohorts
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=10,
        teacher=user,
    )

    future_time = timezone.now() + timezone.timedelta(days=1)
    session = cohort.sessions.create(
        name='Test Session',
        description='Test Description',
        start_time=future_time,
        end_time=future_time + timezone.timedelta(hours=2),
    )

    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_student_dashboard(client, user):
    url = reverse('classes:student-dashboard')

    # Login Required
    response = client.get(url)
    assert response.status_code == 302  # Should redirect to login
    assert '/login' in response['Location']

    # Show dashboard for logged in users
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'classes/dashboard.html')

    # Verify dashboard shows enrolled cohorts
    teacher = User.objects.create(username='teacher', is_staff=True)
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=10,
        teacher=teacher,
    )
    cohort.students.add(user)

    future_time = timezone.now() + timezone.timedelta(days=1)
    session = cohort.sessions.create(
        name='Test Session',
        description='Test Description',
        start_time=future_time,
        end_time=future_time + timezone.timedelta(hours=2),
    )

    assignment = LiveCohortAssignment.objects.create(
        cohort=cohort,
        name='Test Assignment',  # Changed from title to name
        due_date=future_time,
    )

    response = client.get(url)
    assert response.status_code == 200
    assert 'Test Cohort' in str(response.content)
    assert 'Test Session' in str(response.content)
    assert 'Test Assignment' in str(response.content)

    # Verify non-enrolled cohorts don't show up
    other_cohort = LiveCohort.objects.create(
        name='Other Cohort',
        description='Other Description',
        price='99.99',
        max_students=10,
        teacher=teacher,
    )

    response = client.get(url)
    assert 'Other Cohort' not in str(response.content)

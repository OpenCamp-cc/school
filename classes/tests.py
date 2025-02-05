from decimal import Decimal
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed

from users.models import User

from .models import (
    LiveCohort,
    LiveCohortAssignment,
    LiveCohortRegistration,
    LiveCohortSession,
)


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


@pytest.mark.django_db
def test_register_student(client, user):
    teacher = User.objects.create(
        username='teacher', email='teacher@gmail.com', is_staff=True
    )
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=2,
        teacher=teacher,
    )

    # Test successful registration
    registration = LiveCohortRegistration.objects.register_student(cohort, user)
    assert registration.student == user
    assert registration.cohort == cohort
    assert cohort.students.count() == 1

    # Test cohort full
    other_student = User.objects.create(
        username='other_student', email='other_student@gmail.com'
    )
    registration = LiveCohortRegistration.objects.register_student(
        cohort, other_student
    )
    assert cohort.students.count() == 2

    # Try registering when cohort is full
    new_student = User.objects.create(
        username='new_student', email='new_student@gmail.com'
    )
    with pytest.raises(Exception) as exc:
        LiveCohortRegistration.objects.register_student(cohort, new_student)
    assert str(exc.value) == 'Cohort is full'


@pytest.mark.django_db
@patch('classes.models.plunk_client')
def test_register_new_student(mock_plunk, client):
    teacher = User.objects.create(
        username='teacher', email='teacher@gmail.com', is_staff=True
    )
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=2,
        teacher=teacher,
    )

    # Test successful registration
    registration = LiveCohortRegistration.objects.register_new_student(
        cohort=cohort, first_name='John', last_name='Doe', email='john@example.com'
    )

    # Verify user was created
    student = User.objects.get(email='john@example.com')
    assert student.first_name == 'John'
    assert student.last_name == 'Doe'

    # Verify registration
    assert registration.student == student
    assert registration.cohort == cohort

    assert student.signup_invites.count() == 1

    # Verify email was sent
    mock_plunk.send_email.assert_called_once()
    call_args = mock_plunk.send_email.call_args[0]
    assert call_args[0] == ['john@example.com']
    assert 'registration for Test Cohort confirmed' in call_args[1]

    # Test cohort full
    LiveCohortRegistration.objects.register_new_student(
        cohort=cohort, first_name='Jane', last_name='Doe', email='jane@example.com'
    )

    # Try registering when cohort is full
    with pytest.raises(Exception) as exc:
        LiveCohortRegistration.objects.register_new_student(
            cohort=cohort, first_name='Bob', last_name='Smith', email='bob@example.com'
        )
    assert str(exc.value) == 'Cohort is full'


@pytest.mark.django_db
@patch('classes.models.plunk_client')
def test_cohort_students(mock_plunk, client, teacher, user):
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=2,
        teacher=teacher,
    )
    url = reverse('classes:cohort-students', args=[cohort.id])

    # Test unauthorized access
    response = client.get(url)
    assert response.status_code == 302
    assert '/login' in response['Location']

    # Regular user cannot access
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302

    # Staff can access students page
    client.force_login(teacher)
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'classes/students.html')
    assert 'cohort' in response.context
    assert 'form' in response.context
    assert 'students' in response.context

    # Test adding existing student
    existing_student = User.objects.create(
        username='student@test.com',
        email='student@test.com',
    )
    response = client.post(
        url, {'email': 'student@test.com', 'first_name': 'test', 'last_name': 'test'}
    )
    assert response.status_code == 302
    assert cohort.students.filter(id=existing_student.id).exists()

    # Test adding new student
    response = client.post(
        url,
        {
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'Student',
        },
    )
    assert response.status_code == 302
    new_student = User.objects.get(email='new@test.com')
    assert cohort.students.filter(id=new_student.id).exists()
    assert new_student.first_name == 'New'
    assert new_student.last_name == 'Student'

    # Test form validation error
    response = client.post(url, {'email': 'invalid'})
    assert response.status_code == 200
    assert 'Please correct the errors below' in str(response.content)

    # Verify email was sent for new student registration
    mock_plunk.send_email.assert_called_once()


@pytest.mark.django_db
def test_remove_student(client, teacher, user):
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=2,
        teacher=teacher,
    )
    cohort.students.add(user)
    url = reverse('classes:remove-student', args=[cohort.id])

    # Test unauthorized access
    response = client.post(url, {'student_id': user.id})
    assert response.status_code == 302
    assert '/login' in response['Location']
    assert cohort.students.filter(id=user.id).exists()

    # Regular user cannot remove students
    client.force_login(user)
    response = client.post(url, {'student_id': user.id})
    assert response.status_code == 302
    assert cohort.students.filter(id=user.id).exists()

    # Staff can remove students
    client.force_login(teacher)
    response = client.post(url, {'student_id': user.id})
    assert response.status_code == 302
    assert not cohort.students.filter(id=user.id).exists()

    # GET requests should redirect
    response = client.get(url)
    assert response.status_code == 302
    assert str(cohort.id) in response['Location']

    # Invalid student_id should not cause errors
    response = client.post(url, {'student_id': 99999})
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_session(client, teacher, user):
    # Create test data
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=10,
        teacher=teacher,
    )

    future_time = timezone.now() + timezone.timedelta(days=1)
    session = cohort.sessions.create(
        name='Test Session',
        description='Test Description',
        start_time=future_time,
        end_time=future_time + timezone.timedelta(hours=2),
    )

    url = reverse('classes:delete-session', args=[session.id])

    # Test unauthorized access
    response = client.post(url)
    assert response.status_code == 302
    assert '/login' in response['Location']
    assert LiveCohortSession.objects.filter(id=session.id).exists()

    # Regular user cannot delete sessions
    client.force_login(user)
    response = client.post(url)
    assert response.status_code == 302
    assert LiveCohortSession.objects.filter(id=session.id).exists()

    # GET requests should redirect
    response = client.get(url)
    assert response.status_code == 302
    assert str(cohort.id) in response['Location']

    # Staff can delete sessions
    client.force_login(teacher)
    response = client.post(url)
    assert response.status_code == 302
    assert not LiveCohortSession.objects.filter(id=session.id).exists()
    assert str(cohort.id) in response['Location']


@pytest.mark.django_db
def test_cohort_sessions(client, teacher, user):
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=10,
        teacher=teacher,
    )
    url = reverse('classes:cohort-sessions', args=[cohort.id])
    future_time = timezone.now() + timezone.timedelta(days=1)

    # Test unauthorized access
    response = client.get(url)
    assert response.status_code == 302
    assert '/login' in response['Location']

    # Regular user cannot access sessions page
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302

    # Staff can access sessions page
    client.force_login(teacher)
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'classes/sessions.html')

    # Test adding new session
    session_data = {
        'name': 'New Session',
        'description': 'Test Description',
        'start_time': future_time.strftime('%Y-%m-%dT%H:%M'),
        'end_time': (future_time + timezone.timedelta(hours=2)).strftime(
            '%Y-%m-%dT%H:%M'
        ),
    }
    response = client.post(url, session_data)
    assert response.status_code == 302
    assert cohort.sessions.filter(name='New Session').exists()

    # Test invalid form submission
    invalid_data = {
        'name': 'Bad Session',
        'start_time': future_time.strftime('%Y-%m-%dT%H:%M'),
        'end_time': (future_time - timezone.timedelta(hours=2)).strftime(
            '%Y-%m-%dT%H:%M'
        ),
    }
    response = client.post(url, invalid_data)
    assert response.status_code == 200
    assert 'Please correct the errors below' in str(response.content)


@pytest.mark.django_db
def test_cohort_assignments(client, teacher, user):
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=10,
        teacher=teacher,
    )
    url = reverse('classes:cohort-assignments', args=[cohort.id])
    future_time = timezone.now() + timezone.timedelta(days=1)

    # Test unauthorized access
    response = client.get(url)
    assert response.status_code == 302
    assert '/login' in response['Location']

    # Regular user cannot access assignments page
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302

    # Staff can access assignments page
    client.force_login(teacher)
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'classes/assignments.html')

    # Test adding new assignment
    assignment_data = {
        'name': 'New Assignment',
        'description': 'Test Description',
        'due_date': future_time.strftime('%Y-%m-%dT%H:%M'),
    }
    response = client.post(url, assignment_data)
    assert response.status_code == 302
    assert cohort.assignments.filter(name='New Assignment').exists()

    # Test invalid form submission
    invalid_data = {
        'name': '',
        'due_date': 'invalid-date',
    }
    response = client.post(url, invalid_data)
    assert response.status_code == 200
    assert 'Please correct the errors below' in str(response.content)


@pytest.mark.django_db
def test_all_sessions(client, teacher, user):
    # Create test data
    cohort = LiveCohort.objects.create(
        name='Test Cohort',
        description='Test Description',
        price='99.99',
        max_students=10,
        teacher=teacher,
    )

    # Create multiple sessions
    future_time = timezone.now() + timezone.timedelta(days=1)
    session1 = cohort.sessions.create(
        name='Session 1',
        description='First Session',
        start_time=future_time,
        end_time=future_time + timezone.timedelta(hours=2),
    )
    session2 = cohort.sessions.create(
        name='Session 2',
        description='Second Session',
        start_time=future_time + timezone.timedelta(days=1),
        end_time=future_time + timezone.timedelta(days=1, hours=2),
    )

    url = reverse('classes:all-sessions', args=[cohort.id])

    # Test unauthorized access
    response = client.get(url)
    assert response.status_code == 302
    assert '/login' in response['Location']

    # Test access for enrolled student
    cohort.students.add(user)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'classes/sessions_component.html')
    assert 'Session 1' in str(response.content)
    assert 'Session 2' in str(response.content)
    assert response.context['all'] is True

    # Test access for teacher
    client.force_login(teacher)
    response = client.get(url)
    assert response.status_code == 200
    assert 'Session 1' in str(response.content)
    assert 'Session 2' in str(response.content)

    # Test access for non-enrolled user
    other_user = User.objects.create(username='other', email='other@test.com')
    client.force_login(other_user)
    response = client.get(url)
    assert response.status_code == 404

    # Test non-existent cohort
    response = client.get(reverse('classes:all-sessions', args=[99999]))
    assert response.status_code == 404

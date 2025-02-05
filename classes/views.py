from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from users.http import AuthenticatedHttpRequest
from users.models import User

from .forms import AddStudentForm, LiveCohortForm
from .models import (
    LiveCohort,
    LiveCohortAssignment,
    LiveCohortAssignmentSubmission,
    LiveCohortRegistration,
)


def homepage(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def about_us(request: HttpRequest) -> HttpResponse:
    return render(request, 'about_us.html')


def faq(request: HttpRequest) -> HttpResponse:
    return render(request, 'faq.html')


def upcoming_courses(request: HttpRequest) -> HttpResponse:
    return render(request, 'courses.html')


def curriculum(request: HttpRequest) -> HttpResponse:
    return redirect(reverse('classes:courses'))


def search_classes(request: HttpRequest) -> HttpResponse:
    return render(request, 'classes/search_classes.html')


@user_passes_test(lambda u: u.is_staff)
def teacher_dashboard(request: HttpRequest) -> HttpResponse:
    user = request.user

    # Get all classes taught by the user
    live_cohorts = LiveCohort.objects.filter(teacher=user)

    # Get upcoming sessions from live cohorts
    now = timezone.now()
    upcoming_sessions = []
    for cohort in live_cohorts:
        cohort.upcoming_sessions = list(
            cohort.sessions.filter(start_time__gt=now).order_by('start_time')
        )
        cohort.upcoming_assignments = list(
            cohort.assignments.filter(due_date__gt=now).order_by('due_date')
        )

    context = {
        'cohorts': live_cohorts,
        'upcoming_sessions': upcoming_sessions,
    }

    return render(request, 'classes/teacher-dashboard.html', context)


@user_passes_test(lambda u: u.is_staff)
def add_live_cohort(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = LiveCohortForm(request.POST)
        if form.is_valid():
            try:
                cohort = form.save(teacher=request.user)
                return redirect(
                    'classes:teacher-dashboard'
                )  # Changed from teacher-classes
            except Exception as e:
                messages.error(request, 'Failed to create cohort. Please try again.')
        else:
            print(form.errors)
    else:
        form = LiveCohortForm()

    return render(request, 'classes/add_live_cohort.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def cohort_students(request: HttpRequest, id: int) -> HttpResponse:
    cohort = get_object_or_404(LiveCohort, id=id)

    if request.method == 'POST':
        form = AddStudentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                student = User.objects.get(email=data['email'])
            except User.DoesNotExist:
                LiveCohortRegistration.objects.register_new_student(
                    cohort, data['first_name'], data['last_name'], data['email']
                )
            else:
                LiveCohortRegistration.objects.register_student(cohort, student)
            messages.success(request, 'Student added successfully.')
            return redirect('classes:cohort-students', id=id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddStudentForm()

    context = {
        'cohort': cohort,
        'form': form,
        'students': cohort.students.all().order_by('first_name', 'last_name'),
    }
    return render(request, 'classes/students.html', context)


@user_passes_test(lambda u: u.is_staff)
def remove_student(request: HttpRequest, id: int) -> HttpResponse:
    if request.method != 'POST':
        return redirect('classes:cohort-students', id=id)

    cohort = get_object_or_404(LiveCohort, id=id)
    student_id = request.POST.get('student_id')

    try:
        student = User.objects.get(id=student_id)
        if student in cohort.students.all():
            cohort.students.remove(student)
            messages.success(
                request, f'{student.get_full_name()} has been removed from the class.'
            )
    except User.DoesNotExist:
        pass

    return redirect('classes:cohort-students', id=id)


@login_required
def student_dashboard(request: AuthenticatedHttpRequest) -> HttpResponse:
    user = request.user

    # Get all classes enrolled by the user
    live_cohorts = LiveCohort.objects.filter(students=user)

    # Get upcoming sessions from live cohorts
    now = timezone.now()
    upcoming_sessions = {}
    upcoming_assignments = {}

    for cohort in live_cohorts:
        cohort_sessions = cohort.sessions.filter(start_time__gt=now).order_by(
            'start_time'
        )[:4]
        cohort.upcoming_sessions = list(cohort_sessions)

        assignments = LiveCohortAssignment.objects.filter(
            cohort=cohort, due_date__gt=now
        ).order_by('due_date')[:4]
        cohort.upcoming_assignments = list(assignments)

    context = {
        'cohorts': live_cohorts,
    }

    return render(request, 'classes/dashboard.html', context)


@login_required
def all_sessions(request: AuthenticatedHttpRequest, id: int) -> HttpResponse:
    user = request.user
    cohort = get_object_or_404(LiveCohort.objects.filter(students=user), id=id)

    cohort_sessions = cohort.sessions.order_by('start_time')
    cohort.upcoming_sessions = list(cohort_sessions)
    context = {
        'cohort': cohort,
        'all': True,
    }

    return render(request, 'classes/sessions_component.html', context)


@login_required
def all_assignments(request: AuthenticatedHttpRequest, id: int) -> HttpResponse:
    user = request.user
    cohort = get_object_or_404(LiveCohort.objects.filter(students=user), id=id)

    cohort_assignments = cohort.assignments.order_by('due_date')
    cohort.upcoming_assignments = list(cohort_assignments)
    context = {
        'cohort': cohort,
        'all': True,
    }

    return render(request, 'classes/assignments_component.html', context)


@login_required
def view_assignment(request: HttpRequest, id: int) -> HttpResponse:
    assignment = get_object_or_404(LiveCohortAssignment, id=id)
    user = request.user

    # Check if user is enrolled in the cohort
    if user not in assignment.cohort.students.all():
        return redirect('classes:student-dashboard')

    # Get submission if exists
    submission = LiveCohortAssignmentSubmission.objects.filter(
        assignment=assignment, student=user
    ).first()

    context = {
        'assignment': assignment,
        'submission': submission,
    }

    return render(request, 'classes/assignment.html', context)

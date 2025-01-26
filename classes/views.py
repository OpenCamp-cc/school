from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from users.http import AuthenticatedHttpRequest
from users.models import User

from .forms import LiveCohortForm
from .models import LiveCohort, LiveCohortAssignment, LiveCohortAssignmentSubmission


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
        cohort_sessions = cohort.sessions.filter(start_time__gt=now).order_by(
            'start_time'
        )
        upcoming_sessions.extend(cohort_sessions)

    # Sort sessions by start time and limit to next 10
    upcoming_sessions.sort(key=lambda x: x.start_time)
    upcoming_sessions = upcoming_sessions[:10]

    context = {
        'live_cohorts': live_cohorts,
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


@login_required
def student_dashboard(request: HttpRequest) -> HttpResponse:
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

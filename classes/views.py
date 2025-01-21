from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from users.http import AuthenticatedHttpRequest
from users.models import User

from .forms import LiveCohortForm
from .models import LiveCohort


def homepage(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def search_classes(request: HttpRequest) -> HttpResponse:
    return render(request, 'classes/search_classes.html')


def teacher_classes(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, pk=user_id)
    classes = LiveCohort.objects.filter(teacher=user).prefetch_related('sessions')

    return render(
        request,
        'classes/teacher_classes.html',
        {'user': user, 'classes': classes},
    )


@login_required
def add_live_cohort(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = LiveCohortForm(request.POST)
        if form.is_valid():
            try:
                cohort = form.save(teacher=request.user)
                return redirect('classes:teacher-classes', user_id=request.user.id)
            except Exception as e:
                messages.error(request, 'Failed to create cohort. Please try again.')
    else:
        form = LiveCohortForm()

    return render(request, 'classes/add_live_cohort.html', {'form': form})


@login_required
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


@login_required
def student_dashboard(request: HttpRequest) -> HttpResponse:
    user = request.user

    # Get all classes enrolled by the user
    live_cohorts = LiveCohort.objects.filter(students=user)

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

    return render(request, 'classes/dashboard.html', context)

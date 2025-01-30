from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from quizzes.models import (
    ChoiceQuestionSubmission,
    QuestionOption,
    Quiz,
    QuizAttempt,
    QuizChoiceQuestion,
    QuizTextQuestion,
    TextQuestionSubmission,
)
from users.http import AuthenticatedHttpRequest

from .forms import LiveCohortForm
from .models import (
    LiveCohort,
    LiveCohortAssignment,
    LiveCohortAssignmentSubmission,
    LiveCohortQuiz,
    LiveCohortQuizSubmission,
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

        cohort_quizzes = (
            LiveCohortQuiz.objects.filter(cohort=cohort, due_date__gt=now)
            .select_related('quiz')
            .order_by('due_date')[:4]
        )
        cohort.upcoming_quizzes = list(cohort_quizzes)

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


@login_required
def all_quizzes(request: HttpRequest, id: int) -> HttpResponse:
    user = request.user
    cohort = get_object_or_404(LiveCohort.objects.filter(students=user), id=id)

    cohort_quizzes = cohort.quizzes.order_by('due_date')
    cohort.upcoming_quizzes = list(cohort_quizzes)
    context = {
        'cohort': cohort,
        'all': True,
    }

    return render(request, 'classes/quizzes_component.html', context)


@login_required
def view_quiz(request: HttpRequest, id: int) -> HttpResponse:
    quiz = get_object_or_404(Quiz, id=id)
    user = request.user

    cohort_quiz = (
        LiveCohortQuiz.objects.filter(quiz=quiz)
        .select_related('cohort', 'quiz')
        .prefetch_related(
            Prefetch(
                'quiz__choice_questions',
                queryset=QuizChoiceQuestion.objects.select_related(
                    'question'
                ).prefetch_related(
                    'question__options',
                    Prefetch(
                        'question__choicequestionsubmission_set',
                        queryset=ChoiceQuestionSubmission.objects.filter(
                            quiz_attempt__student=user, quiz_attempt__quiz=quiz
                        )
                        .select_related('quiz_attempt')
                        .order_by('-quiz_attempt__completed_at'),
                        to_attr='latest_submission',
                    ),
                ),
            ),
            Prefetch(
                'quiz__text_questions',
                queryset=QuizTextQuestion.objects.select_related(
                    'question'
                ).prefetch_related(
                    Prefetch(
                        'question__textquestionsubmission_set',
                        queryset=TextQuestionSubmission.objects.filter(
                            quiz_attempt__student=user, quiz_attempt__quiz=quiz
                        )
                        .select_related('quiz_attempt')
                        .order_by('-quiz_attempt__completed_at'),
                        to_attr='latest_submission',
                    )
                ),
            ),
            Prefetch(
                'submissions',
                queryset=LiveCohortQuizSubmission.objects.select_related('quiz_attempt')
                .filter(quiz_attempt__student=user)
                .order_by('-quiz_attempt__completed_at'),
                to_attr='latest_submission',
            ),
        )
        .first()
    )

    if not cohort_quiz:
        return redirect('classes:student-dashboard')

    # Check if user is enrolled in the cohort
    if user not in cohort_quiz.cohort.students.all():
        return redirect('classes:student-dashboard')

    if request.method == 'POST':
        print('POST')
        # Check if multiple attempts are allowed
        latest_submission = (
            cohort_quiz.latest_submission[0] if cohort_quiz.latest_submission else None
        )
        if latest_submission and not cohort_quiz.quiz.allow_multiple_attempts:
            messages.error(request, 'Multiple attempts are not allowed for this quiz.')
            return redirect('classes:student-dashboard')

        try:
            with transaction.atomic():
                print(1)
                attempt = QuizAttempt.objects.create(
                    quiz=cohort_quiz.quiz, student=user
                )
                earned_points = 0

                # Handle choice questions
                for quiz_question in cohort_quiz.quiz.choice_questions.all():
                    question = quiz_question.question
                    option_ids = request.POST.getlist(f'choice_{question.id}')

                    selected_options = QuestionOption.objects.filter(id__in=option_ids)
                    correct_options = set(question.options.filter(is_correct=True))
                    is_correct = set(selected_options) == correct_options

                    submission = ChoiceQuestionSubmission.objects.create(
                        quiz_attempt=attempt, question=question, is_correct=is_correct
                    )
                    submission.selected_options.set(selected_options)

                    if is_correct:
                        earned_points += quiz_question.points

                # Handle text questions
                for quiz_question in cohort_quiz.quiz.text_questions.all():
                    question = quiz_question.question
                    answer = request.POST.get(f'text_{question.id}', '').strip()

                    is_correct = False
                    if answer:
                        if question.is_case_sensitive:
                            is_correct = (
                                answer == question.answer
                                or answer in question.alternative_answers
                            )
                        else:
                            answer_lower = answer.lower()
                            is_correct = (
                                answer_lower == question.answer.lower()
                                or answer_lower
                                in [ans.lower() for ans in question.alternative_answers]
                            )

                    TextQuestionSubmission.objects.create(
                        quiz_attempt=attempt,
                        question=question,
                        answer=answer,
                        is_correct=is_correct,
                    )

                    if is_correct:
                        earned_points += quiz_question.points

                # Calculate and save final score
                attempt.score = earned_points
                attempt.completed_at = timezone.now()
                attempt.save()

                # Create quiz submission record for the course
                LiveCohortQuizSubmission.objects.create(
                    cohort_quiz=cohort_quiz, quiz_attempt=attempt
                )

                messages.success(request, 'Quiz submitted successfully!')
                return redirect('classes:quiz', id=id)

        except Exception as e:
            messages.error(
                request, f'An error occurred while submitting the quiz: {str(e)}'
            )
            return redirect('classes:quiz', id=id)

    return render(request, 'classes/quiz.html', {'cohort_quiz': cohort_quiz})

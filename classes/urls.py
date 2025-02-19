from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.homepage, name='index'),
    path('about-us', views.about_us, name='about-us'),
    path('courses', views.upcoming_courses, name='courses'),
    path('faq', views.faq, name='faq'),
    path('docs/curriculum/', views.curriculum, name='curriculum'),
    path('classes', views.search_classes, name='search-classes'),
    path(
        'teacher', RedirectView.as_view(url='/teacher/dashboard/'), name='teacher-main'
    ),
    path('teacher/dashboard/live/add', views.add_live_cohort, name='add-live-cohort'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher-dashboard'),
    path('dashboard/', views.student_dashboard, name='student-dashboard'),
    path('cohort/<int:id>/all-sessions', views.all_sessions, name='all-sessions'),
    path(
        'cohort/<int:id>/all-assignments', views.all_assignments, name='all-assignments'
    ),
    path('cohort/<int:id>/students', views.cohort_students, name='cohort-students'),
    path(
        'cohort/<int:id>/students/remove', views.remove_student, name='remove-student'
    ),
    path('assignment/<int:id>', views.view_assignment, name='assignment'),
    path(
        'cohort/<int:id>/assignments',
        views.cohort_assignments,
        name='cohort-assignments',
    ),
    path(
        'assignment/<int:id>/edit',
        views.edit_assignment,
        name='edit-assignment',
    ),
    path(
        'cohort/<int:id>/sessions',
        views.cohort_sessions,
        name='cohort-sessions',
    ),
    path(
        'session/<int:id>/edit',
        views.edit_session,
        name='edit-session',
    ),
    path(
        'session/<int:id>/delete',
        views.delete_session,
        name='delete-session',
    ),
    path(
        'cohort/<int:id>/edit',
        views.edit_live_cohort,
        name='edit-live-cohort',
    ),
    path('cohort/<int:id>/all-quizzes/', views.all_quizzes, name='all-quizzes'),
]

from django.urls import path

from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.homepage, name='index'),
    path('about-us', views.about_us, name='about-us'),
    path('courses', views.upcoming_courses, name='courses'),
    path('faq', views.faq, name='faq'),
    path('docs/curriculum/', views.curriculum, name='curriculum'),
    path('classes', views.search_classes, name='search-classes'),
    path('teacher/dashboard/live/add', views.add_live_cohort, name='add-live-cohort'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher-dashboard'),
    path('dashboard/', views.student_dashboard, name='student-dashboard'),
    path('cohort/<int:id>/all-sessions', views.all_sessions, name='all-sessions'),
    path(
        'cohort/<int:id>/all-assignments', views.all_assignments, name='all-assignments'
    ),
    path('assignment/<int:id>', views.view_assignment, name='assignment'),
    path('cohort/<int:id>/all-quizzes/', views.all_quizzes, name='all-quizzes'),
    path('quiz/<int:id>/', views.view_quiz, name='quiz'),
]

from django.urls import path

from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.homepage, name='index'),
    path('classes', views.search_classes, name='search-classes'),
    path('dashboard/live/add', views.add_live_cohort, name='add-live-cohort'),
    path(
        'dashboard/private/add', views.add_private_package, name='add-private-package'
    ),
    path(
        'teacher/<int:user_id>/classes', views.teacher_classes, name='teacher-classes'
    ),
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
]

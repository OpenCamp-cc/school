from django.urls import path

from . import views

app_name = 'landing'

urlpatterns = [
    path('profile', views.profile, name='profile'),
    path('profile/admin', views.profile_admin, name='profile_admin'),
    path('landing/profile/create', views.create_profile, name='create_profile'),
    path('landing/profile/update', views.update_profile, name='update_profile'),
    path(
        'profile/update-image', views.update_profile_image, name='update_profile_image'
    ),
    path(
        'landing/profile/links/create',
        views.create_profile_link,
        name='create_profile_link',
    ),
    path(
        'landing/profile/links/<int:link_id>/update',
        views.update_profile_link,
        name='update_profile_link',
    ),
    path(
        'landing/profile/links/<int:link_id>/toggle-visibility',
        views.toggle_link_visibility,
        name='toggle_link_visibility',
    ),
    path(
        'landing/profile/links/<int:link_id>/archive',
        views.archive_link,
        name='archive_link',
    ),
    path(
        'landing/profile/links/<int:link_id>/restore',
        views.restore_link,
        name='restore_link',
    ),
    path(
        'landing/profile/links/<int:link_id>/delete',
        views.delete_link,
        name='delete_link',
    ),
    path(
        'landing/profile/collections/create',
        views.create_profile_category,
        name='create_profile_category',
    ),
    path(
        'landing/profile/collections/<int:category_id>/update',
        views.update_profile_category,
        name='update_profile_category',
    ),
    path(
        'landing/profile/collections/<int:category_id>/toggle-visibility',
        views.toggle_category_visibility,
        name='toggle_category_visibility',
    ),
    path(
        'landing/profile/collections/<int:category_id>/delete',
        views.delete_category,
        name='delete_category',
    ),
    path(
        'profile/links/update-order/',
        views.update_links_order,
        name='update_links_order',
    ),
    path(
        'profile/categories/update-order/',
        views.update_categories_order,
        name='update_categories_order',
    ),
    path(
        'profile/links/update-category/',
        views.update_link_category,
        name='update_link_category',
    ),
    path(
        'profile/links/<int:link_id>/click/',
        views.update_link_click_count,
        name='update_link_click_count',
    ),
]

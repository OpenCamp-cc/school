from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import URLValidator
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import ProfileCategoryForm, ProfileForm, ProfileImageForm, ProfileLinkForm
from .inputs import ProfileCategoryInput, ProfileInput, ProfileLinkInput
from .models.profiles import Profile, ProfileCategory, ProfileLink
from .service import ProfileService

SOCIAL_LINKS = [
    ('threads', 'threads_url'),
    ('instagram', 'instagram_url'),
    ('facebook', 'facebook_url'),
    ('youtube', 'youtube_url'),
    ('twitter', 'twitter_url'),
    ('email', 'email_url'),
    ('website', 'website_url'),
]


def _render_profile(request, template_name, context):
    return render(request, f'landing/{template_name}', context)


def profile(request):
    profile = Profile.objects.prefetch_related(
        Prefetch(
            'profilecategory_set',
            queryset=ProfileCategory.objects.filter(is_deleted=False)
            .prefetch_related(
                Prefetch(
                    'categorized_links',
                    queryset=ProfileLink.objects.filter(
                        is_deleted=False,
                    ).order_by('-order'),
                )
            )
            .order_by('-order'),
            to_attr='categories',
        ),
        Prefetch(
            'profilelink_set',
            queryset=ProfileLink.objects.filter(
                is_deleted=False, profile_category__isnull=True
            ).order_by('-order'),
            to_attr='active_uncategorized_links',
        ),
        Prefetch(
            'profilelink_set',
            queryset=ProfileLink.objects.filter(is_deleted=True).order_by('-order'),
            to_attr='archived_links',
        ),
    ).get(user_id=request.user.id)

    active_links = [
        {'name': name, 'url': getattr(profile, url_field)}
        for name, url_field in SOCIAL_LINKS
        if getattr(profile, url_field)
    ]

    context = {'profile': profile, 'active_links': active_links}

    return _render_profile(request, 'profile.html', context)


@login_required
def profile_admin(request):
    try:
        profile = Profile.objects.prefetch_related(
            Prefetch(
                'profilecategory_set',
                queryset=ProfileCategory.objects.filter(is_deleted=False)
                .prefetch_related(
                    Prefetch(
                        'categorized_links',
                        queryset=ProfileLink.objects.filter(
                            is_deleted=False,
                        ).order_by('-order'),
                    )
                )
                .order_by('-order'),
                to_attr='categories',
            ),
            Prefetch(
                'profilelink_set',
                queryset=ProfileLink.objects.filter(
                    is_deleted=False, profile_category__isnull=True
                ).order_by('-order'),
                to_attr='active_uncategorized_links',
            ),
            Prefetch(
                'profilelink_set',
                queryset=ProfileLink.objects.filter(is_deleted=True).order_by('-order'),
                to_attr='archived_links',
            ),
        ).get(user_id=request.user.id)

    except Profile.DoesNotExist:
        return redirect('landing:create_profile')

    form = ProfileForm(
        data=request.POST or None, files=request.FILES or None, instance=profile
    )

    if request.method == 'POST':
        if form.is_valid():
            try:
                profile_input = ProfileInput(**form.cleaned_data)
                ProfileService().update_profile(
                    request.user.id, profile.id, profile_input
                )
                messages.success(request, 'Profile updated successfully')

            except Exception as e:
                messages.error(request, f'Failed to update profile. Error: {e}')

        else:
            messages.error(request, f'Failed to update profile. Error: {form.errors}')

        return redirect('landing:profile_admin')

    active_links = [
        {'name': name, 'url': getattr(profile, url_field)}
        for name, url_field in SOCIAL_LINKS
        if getattr(profile, url_field)
    ]
    inactive_links = [
        {'name': name}
        for name, url_field in SOCIAL_LINKS
        if not getattr(profile, url_field)
    ]

    return _render_profile(
        request,
        'profile_admin.html',
        {
            'form': form,
            'profile': profile,
            'active_links': active_links,
            'inactive_links': inactive_links,
        },
    )


@login_required
def create_profile(request):
    if hasattr(request.user, 'landing_profile'):
        return redirect('landing:update_profile')

    form = ProfileForm(data=request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form_data = form.cleaned_data.copy()

            if 'profile_image' in form.files:
                form_data['profile_image'] = form.files['profile_image']

            profile_input = ProfileInput(**form_data)

            try:
                ProfileService().create_profile(request.user.id, profile_input)

                return redirect('landing:admin')

            except Exception:
                return redirect('/')

    return _render_profile(request, 'create_profile.html', {'form': form})


@login_required
def update_profile(request):
    try:
        profile = request.user.landing_profile
    except Profile.DoesNotExist:
        return redirect('landing:create_profile')

    form = ProfileForm(data=request.POST or None, instance=profile)

    if request.method == 'POST':
        if form.is_valid():
            profile_input = ProfileInput(**form.cleaned_data)
            try:
                ProfileService().update_profile(
                    request.user.id, profile.id, profile_input
                )
                return redirect('landing:profile_admin')
            except Exception:
                return redirect('/')
        else:
            print('Form errors:', form.errors)

    return _render_profile(
        request, 'update_profile.html', {'form': form, 'profile': profile}
    )


@login_required
def update_profile_image(request):
    try:
        profile = request.user.landing_profile
        if (
            request.method == 'POST'
            and request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        ):
            form = ProfileImageForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    ProfileService().update_profile_image(
                        profile_id=profile.id,
                        image=form.cleaned_data['profile_image'],
                    )
                    return JsonResponse(
                        {'is_successful': True, 'url': profile.profile_image.url}
                    )
                except Exception as e:
                    return JsonResponse({'is_successful': False, 'message': str(e)})
            else:
                return JsonResponse(
                    {
                        'is_successful': False,
                        'message': ' '.join(form.errors['profile_image']),
                    }
                )

        return JsonResponse({'is_successful': False, 'message': 'Invalid request'})

    except Profile.DoesNotExist:
        return JsonResponse({'is_successful': False, 'message': 'Profile not found'})


@login_required
def create_profile_link(request):
    if request.method != 'POST':
        return redirect('landing:profile_admin')

    if request.method == 'POST':
        try:
            profile = request.user.landing_profile
        except Profile.DoesNotExist:
            return redirect('landing:create_profile')

        form = ProfileLinkForm(data=request.POST or None)
        if form.is_valid():
            try:
                url = form.cleaned_data['url']
                url_validator = URLValidator()
                url_validator(url)

                profile_link_input = ProfileLinkInput(**form.cleaned_data)
                ProfileService().create_profile_link(
                    profile_id=profile.id, profile_link_input=profile_link_input
                )
                messages.success(request, 'Create link successfully')

            except Exception as e:
                messages.error(request, f'Failed to create link. Error: {e}')

        else:
            messages.error(request, f'Failed to create link. Error: {form.errors}')

        return redirect('landing:profile_admin')


@login_required
def update_profile_link(request, link_id):
    if request.method != 'POST':
        return redirect('landing:profile_admin')

    try:
        link = ProfileLink.objects.get(id=link_id)
        form = ProfileLinkForm(request.POST, instance=link)

        if form.is_valid():
            try:
                profile_link_input = ProfileLinkInput(**form.cleaned_data)
                ProfileService().update_profile_link(
                    link_id=link_id, profile_link_input=profile_link_input
                )
                messages.success(request, 'Link updated successfully')
                return redirect('landing:profile_admin')

            except Exception as e:
                messages.error(request, f'Update failed: {str(e)}')
                return redirect('landing:profile_admin')
        else:
            messages.error(request, 'Form validation failed')
            return redirect('landing:profile_admin')

    except ProfileLink.DoesNotExist:
        messages.error(request, 'Link not found')
        return redirect('landing:profile_admin')


@login_required
def toggle_link_visibility(request, link_id):
    try:
        is_hidden = request.POST.get('is_hidden') == 'true'
        ProfileService().toggle_link_visibility(link_id=link_id, is_hidden=is_hidden)
        messages.success(request, 'Link updated successfully')
        return redirect('landing:profile_admin')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('landing:profile_admin')


@login_required
def archive_link(request, link_id):
    try:
        ProfileService().archive_link(link_id=link_id)
        messages.success(request, 'Link updated successfully')
        return redirect('landing:profile_admin')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('landing:profile_admin')


@login_required
def restore_link(request, link_id):
    try:
        ProfileService().restore_link(link_id=link_id)
        messages.success(request, 'Link updated successfully')
        return redirect('landing:profile_admin')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('landing:profile_admin')


@login_required
def delete_link(request, link_id):
    try:
        ProfileService().delete_link(link_id=link_id)
        messages.success(request, 'Link deleted successfully')
        return redirect('landing:profile_admin')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('landing:profile_admin')


@login_required
def create_profile_category(request):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method')
        return redirect('landing:profile_admin')

    if request.method == 'POST':
        try:
            profile = request.user.landing_profile
        except Profile.DoesNotExist:
            messages.error(
                request, 'Please create your profile first before proceeding.'
            )
            return redirect('landing:create_profile')

        ProfileService().create_profile_category(profile_id=profile.id)
        return redirect('landing:profile_admin')


@login_required
def update_profile_category(request, category_id):
    if request.method != 'POST':
        return redirect('landing:profile_admin')

    try:
        profile = request.user.landing_profile
        category = ProfileCategory.objects.get(id=category_id, profile=profile)
        form = ProfileCategoryForm(request.POST, instance=category)

        if form.is_valid():
            try:
                profile_category_input = ProfileCategoryInput(**form.cleaned_data)
                profile_service = ProfileService()
                profile_service.update_profile_category(
                    category_id=category_id,
                    profile_category_input=profile_category_input,
                )
                messages.success(request, 'Category updated successfully')
            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Invalid form data')

    except ProfileCategory.DoesNotExist:
        messages.error(request, 'Category not found')

    return redirect('landing:profile_admin')


@login_required
def toggle_category_visibility(request, category_id):
    if request.method != 'POST':
        return redirect('landing:profile_admin')

    try:
        is_hidden = request.POST.get('is_hidden') == 'true'
        ProfileService().toggle_category_visibility(
            category_id=category_id, is_hidden=is_hidden
        )
        messages.success(request, 'Category visibility updated successfully')
        return redirect('landing:profile_admin')

    except ProfileCategory.DoesNotExist:
        messages.error(request, 'Category not found')
        return redirect('landing:profile_admin')


@login_required
def delete_category(request, category_id):
    try:
        ProfileService().delete_category(category_id=category_id)
        messages.success(request, 'Delete category successfully')
        return redirect('landing:profile_admin')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('landing:profile_admin')


@login_required
def update_links_order(request):
    if request.method == 'POST':
        ordering = request.POST.get('ordering', '')
        if ordering:
            try:
                link_ids = [int(id) for id in ordering.split(',') if id.strip()]
                if link_ids:
                    ProfileService().update_links_order(link_ids)
                    messages.success(request, 'Link order updated successfully')
            except Exception as e:
                print(f'Exception: {e}')
                messages.error(request, f'Failed to update link order: {str(e)}')

    return redirect('landing:profile_admin')


@login_required
def update_categories_order(request):
    if request.method == 'POST':
        ordering = request.POST.get('ordering', '')
        if ordering:
            try:
                category_ids = [int(id) for id in ordering.split(',') if id.strip()]
                if category_ids:
                    ProfileService().update_categories_order(category_ids)
                    messages.success(request, 'Category order updated successfully')
            except Exception as e:
                print(f'Exception: {e}')
                messages.error(request, f'Failed to update category order: {str(e)}')

    return redirect('landing:profile_admin')


@require_POST
def update_link_category(request):
    link_id = request.POST.get('link_id')
    category_id = request.POST.get('category_id')

    try:
        service = ProfileService()
        service.update_link_category(
            link_id=int(link_id) if link_id else None,
            category_id=int(category_id) if category_id else None,
            profile=request.user.landing_profile,
        )
        messages.success(request, "Link's category updated successfully")
    except Exception as e:
        print(f'Exception: {e}')
        messages.error(request, f"Failed to update link's category: {str(e)}")

    return redirect('landing:profile_admin')


@csrf_exempt
def update_link_click_count(request, link_id):
    try:
        service = ProfileService()
        service.update_link_click_count(link_id)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        print(f'Exception: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

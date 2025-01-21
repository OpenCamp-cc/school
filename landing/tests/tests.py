import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from landing.inputs import ProfileCategoryInput, ProfileLinkInput
from landing.models.profiles import Profile, ProfileCategory, ProfileLink
from landing.service import ProfileService


@pytest.mark.django_db
class TestOrderable:
    def test_first_item_order(self, profile):
        """Check if first item's order is 0"""

        category = ProfileCategory.objects.create(profile=profile)
        assert category.order == 0

    def test_subsequent_items_order(self, profile):
        """Verify incremental ordering of subsequent items"""

        categories = [
            ProfileCategory.objects.create(profile=profile, title=f'Category {i}')
            for i in range(3)
        ]
        assert [cat.order for cat in categories] == [0, 1, 2]

    def test_update_existing_item(self, category):
        """Verify order remains unchanged when updating existing item"""

        original_order = category.order
        category.title = 'Updated Title'
        category.save()
        category.refresh_from_db()
        assert category.order == original_order

    def test_separate_ordering_for_different_profiles(self, profile, another_profile):
        """Verify independent ordering for different profiles"""

        cat1 = ProfileCategory.objects.create(profile=profile)
        cat2 = ProfileCategory.objects.create(profile=another_profile)
        assert cat1.order == cat2.order == 0

    def test_custom_category_order(self, profile):
        """Test custom order for categories"""

        cat3 = ProfileCategory.objects.create(profile=profile, title='Cat 3', order=5)
        cat1 = ProfileCategory.objects.create(profile=profile, title='Cat 1', order=1)
        cat2 = ProfileCategory.objects.create(profile=profile, title='Cat 2', order=3)

        categories = ProfileCategory.objects.filter(profile=profile).order_by('order')
        assert [cat.title for cat in categories] == ['Cat 1', 'Cat 2', 'Cat 3']
        assert [cat.order for cat in categories] == [1, 3, 5]

    def test_custom_link_order(self, profile, category):
        """Test custom order for links within category"""
        link3 = ProfileLink.objects.create(
            profile=profile,
            profile_category=category,
            title='Link 3',
            url='https://example.com/3',
            order=5,
        )
        link1 = ProfileLink.objects.create(
            profile=profile,
            profile_category=category,
            title='Link 1',
            url='https://example.com/1',
            order=1,
        )
        link2 = ProfileLink.objects.create(
            profile=profile,
            profile_category=category,
            title='Link 2',
            url='https://example.com/2',
            order=3,
        )

        links = ProfileLink.objects.filter(profile_category=category).order_by('order')

        assert [link.title for link in links] == ['Link 1', 'Link 2', 'Link 3']
        assert [link.order for link in links] == [1, 3, 5]

    def test_reorder_categories(self, profile):
        """Test reordering existing categories"""
        # 創建三個分類
        cat1 = ProfileCategory.objects.create(profile=profile, title='Cat 1', order=0)
        cat2 = ProfileCategory.objects.create(profile=profile, title='Cat 2', order=1)
        cat3 = ProfileCategory.objects.create(profile=profile, title='Cat 3', order=2)

        # 將第一個分類移到最後
        cat1.order = 3
        cat1.save()

        categories = ProfileCategory.objects.filter(profile=profile).order_by('order')
        assert [cat.title for cat in categories] == ['Cat 2', 'Cat 3', 'Cat 1']

    def test_reorder_links(self, profile, category):
        """Test reordering existing links"""

        link1 = ProfileLink.objects.create(
            profile=profile,
            profile_category=category,
            title='Link 1',
            url='https://example.com/1',
            order=0,
        )
        link2 = ProfileLink.objects.create(
            profile=profile,
            profile_category=category,
            title='Link 2',
            url='https://example.com/2',
            order=1,
        )
        link3 = ProfileLink.objects.create(
            profile=profile,
            profile_category=category,
            title='Link 3',
            url='https://example.com/3',
            order=2,
        )
        link2.order = 3
        link2.save()

        links = ProfileLink.objects.filter(profile_category=category).order_by('order')
        assert [link.title for link in links] == ['Link 1', 'Link 3', 'Link 2']


@pytest.mark.django_db
class TestProfile:
    def test_profile_creation(self, profile):
        """Test basic profile creation"""

        assert profile.name == 'Test User'
        assert profile.bio == 'Test Bio'
        assert str(profile) == 'Test User'

    def test_profile_update(self, profile):
        """Test profile update functionality"""

        profile.name = 'Updated Name'
        profile.bio = 'Updated Bio'
        profile.save()
        profile.refresh_from_db()

        assert profile.name == 'Updated Name'
        assert profile.bio == 'Updated Bio'

    def test_profile_user_relationship(self, profile, user):
        """Test profile-user relationship"""

        assert profile.user == user
        assert user.landing_profile == profile

    def test_profile_create_api(self, admin_client):
        """Test profile creation through API"""

        url = reverse('landing:create_profile')
        response = admin_client.get(url)
        assert response.status_code == 200

        data = {
            'name': 'Test User',
            'bio': 'Test Bio',
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == 302
        assert Profile.objects.filter(name='Test User').exists()

    def test_profile_update_api(self, admin_client, admin_user):
        """Test profile update through API"""

        profile = Profile.objects.create(
            name='Test User', bio='Old Bio', user=admin_user
        )
        url = reverse('landing:update_profile')
        response = admin_client.get(url)
        assert response.status_code == 200

        data = {
            'name': 'Updated User',
            'bio': 'Updated Bio',
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == 302

        profile.refresh_from_db()
        assert profile.name == 'Updated User'
        assert profile.bio == 'Updated Bio'

    def test_profile_view(self, client, profile):
        """Test profile view page"""

        client.force_login(profile.user)
        url = reverse('landing:profile')
        response = client.get(url)
        assert response.status_code == 200
        assert 'profile' in response.context
        assert response.context['profile'] == profile

    def test_profile_admin_view(self, client, profile):
        """Test profile admin view page"""

        client.force_login(profile.user)
        url = reverse('landing:profile_admin')
        response = client.get(url)
        assert response.status_code == 200
        assert 'profile' in response.context
        assert 'form' in response.context
        assert 'active_links' in response.context
        assert 'inactive_links' in response.context


@pytest.mark.django_db
class TestProfileCategory:
    def test_category_creation(self, category, profile):
        """Test category creation and defaults"""

        assert category.profile == profile
        assert category.title == 'Test Category'
        assert category.order == 0
        assert not category.is_hidden
        assert not category.is_deleted

    def test_category_ordering(self, profile):
        """Test category ordering within profile"""

        categories = [
            ProfileCategory.objects.create(profile=profile, title=f'Cat {i}')
            for i in range(3)
        ]
        assert [cat.order for cat in categories] == [0, 1, 2]

    def test_category_str_representation(self, category):
        """Test category string representation"""

        assert str(category) == 'Test Category'

    def test_category_create_api(self, admin_client, admin_user):
        """Test category creation through API"""

        admin_client.force_login(admin_user)
        profile = Profile.objects.create(name='Test User', user=admin_user)
        url = reverse('landing:create_profile_category')

        response = admin_client.get(url)
        assert response.status_code == 302
        assert response.url == reverse('landing:profile_admin')

        data = {
            'title': 'Test Category',
            'profile': profile.id,
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == 302
        assert response.url == reverse('landing:profile_admin')

    def test_update_category_api(self, admin_client, admin_user, category):
        """Test category update through API"""

        if not hasattr(admin_user, 'landing_profile'):
            Profile.objects.create(user=admin_user, name='Admin User')

        admin_client.force_login(admin_user)
        url = reverse('landing:update_profile_category', args=[category.id])
        data = {'title': 'Updated Category Title'}

        response = admin_client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse('landing:profile_admin')

    def test_toggle_category_visibility(self, admin_client, category):
        """Test toggling category visibility"""

        url = reverse('landing:toggle_category_visibility', args=[category.id])

        # Test hiding
        response = admin_client.post(url, {'is_hidden': 'true'})
        assert response.status_code == 302
        category.refresh_from_db()
        assert category.is_hidden == True

        # Test showing
        response = admin_client.post(url, {'is_hidden': 'false'})
        assert response.status_code == 302
        category.refresh_from_db()
        assert category.is_hidden == False

    def test_delete_category(self, category, profile):
        """Test category deletion using service"""

        service = ProfileService()

        # Create test link
        first_link = service.create_profile_link(
            profile_id=profile.id,
            profile_link_input=ProfileLinkInput(
                title='Test Link 1',
                url='https://example.com/1',
                profile_category_id=category.id,
            ),
        )

        # Delete category
        service.delete_category(category_id=category.id)

        # Check category is deleted from DB
        with pytest.raises(ProfileCategory.DoesNotExist):
            ProfileCategory.objects.get(id=category.id)

        # Check link status after category delete
        first_link.refresh_from_db()
        assert first_link.profile_category is None

    def test_update_categories_order(self, profile):
        """Test category order update using service"""

        service = ProfileService()

        # Create categories with titles
        cat1 = ProfileCategory.objects.create(
            profile=profile,
            title='Cat 1',
            order=0,
        )
        cat2 = ProfileCategory.objects.create(
            profile=profile,
            title='Cat 2',
            order=1,
        )
        cat3 = ProfileCategory.objects.create(
            profile=profile,
            title='Cat 3',
            order=2,
        )

        # Change order
        service.update_categories_order([cat3.id, cat2.id, cat1.id])

        # Verify order
        updated_categories = ProfileCategory.objects.filter(profile=profile).order_by(
            'order'
        )
        assert [c.title for c in updated_categories] == ['Cat 1', 'Cat 2', 'Cat 3']


@pytest.mark.django_db
class TestProfileLink:
    def test_categorized_link_creation(self, categorized_link, category, profile):
        """Test link creation with category"""

        assert categorized_link.profile == profile
        assert categorized_link.profile_category == category
        assert categorized_link.order == 0

    def test_uncategorized_link_creation(self, uncategorized_link, profile):
        """Test link creation without category"""

        assert uncategorized_link.profile == profile
        assert uncategorized_link.profile_category is None
        assert uncategorized_link.order == 0

    def test_link_profile_validation(self, category, another_profile):
        """Test validation of link's profile matching category's profile"""

        with pytest.raises(ValidationError):
            ProfileLink.objects.create(
                profile=another_profile, profile_category=category, title='Invalid Link'
            )

    def test_mixed_links_ordering(self, profile, category, another_category):
        """Test ordering of both categorized and uncategorized links"""

        cat1_links = [
            ProfileLink.objects.create(
                profile=profile,
                profile_category=category,
                title=f'Cat1 Link {i}',
                url=f'https://example.com/cat1/{i}',
                order=i,
            )
            for i in range(2)
        ]
        cat2_links = [
            ProfileLink.objects.create(
                profile=profile,
                profile_category=another_category,
                title=f'Cat2 Link {i}',
                url=f'https://example.com/cat2/{i}',
                order=i,
            )
            for i in range(2)
        ]
        uncategorized_links = [
            ProfileLink.objects.create(
                profile=profile,
                title=f'Uncat Link {i}',
                url=f'https://example.com/uncat/{i}',
                order=i,
            )
            for i in range(2)
        ]

        assert [link.order for link in cat1_links] == [0, 1]
        assert [link.order for link in cat2_links] == [0, 1]
        assert [link.order for link in uncategorized_links] == [0, 1]
        assert ProfileLink.objects.filter(profile=profile).count() == 6

    def test_create_link_with_category_api(self, admin_client, admin_user):
        """Test link creation with category through API"""

        admin_client.force_login(admin_user)
        profile = Profile.objects.create(name='Test User', user=admin_user)
        category = ProfileCategory.objects.create(
            title='Test Category', profile=profile
        )
        url = reverse('landing:create_profile_link')

        response = admin_client.get(url)
        assert response.status_code == 302
        assert response.url == reverse('landing:profile_admin')

        data = {
            'title': 'Test Link',
            'url': 'https://example.com',
            'profile_category': category.id,
            'profile': profile.id,
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == 302
        assert response.url == reverse('landing:profile_admin')

    def test_create_link_without_category_api(self, admin_client, admin_user):
        """Test link creation without category through API"""

        profile = Profile.objects.create(name='Test User', user=admin_user)
        url = reverse('landing:create_profile_link')
        data = {
            'title': 'Test Link',
            'url': 'https://example.com',
            'profile': profile.id,
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == 302

        created_link = ProfileLink.objects.get(title='Test Link')
        assert created_link.profile == profile
        assert created_link.profile_category is None

    def test_update_link_api(self, admin_client, categorized_link):
        """Test link update through API"""

        url = reverse('landing:update_profile_link', args=[categorized_link.id])
        data = {'title': 'Updated Link', 'url': 'https://example.com/updated'}

        response = admin_client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse('landing:profile_admin')

        categorized_link.refresh_from_db()
        assert categorized_link.title == 'Updated Link'
        assert categorized_link.url == 'https://example.com/updated'

    def test_archive_and_restore_link(self, admin_client, admin_user, categorized_link):
        """Test archiving and restoring link"""

        if not hasattr(admin_user, 'landing_profile'):
            Profile.objects.create(user=admin_user, name='Admin User')

        admin_client.force_login(admin_user)
        category = categorized_link.profile_category

        # Test archiving
        archive_url = reverse('landing:archive_link', args=[categorized_link.id])
        response = admin_client.post(archive_url)
        assert response.status_code == 302

        categorized_link.refresh_from_db()
        assert categorized_link.is_deleted is True
        assert categorized_link.profile_category == category

        # Test restoring
        restore_url = reverse('landing:restore_link', args=[categorized_link.id])
        response = admin_client.post(restore_url)
        assert response.status_code == 302

        categorized_link.refresh_from_db()
        assert categorized_link.is_deleted is False
        assert categorized_link.profile_category == category

    def test_update_link_click_count(self, admin_client, categorized_link):
        """Test updating link click count"""

        url = reverse('landing:update_link_click_count', args=[categorized_link.id])

        initial_count = categorized_link.click_count
        response = admin_client.post(url)
        assert response.status_code == 200

        categorized_link.refresh_from_db()
        assert categorized_link.click_count == initial_count + 1

    def test_update_links_order(self, profile, category):
        """Test updating links order using service"""

        # 直接創建 ProfileLink 而不是使用 service.create_profile_link
        link1 = ProfileLink.objects.create(
            profile=profile,
            profile_category=category,
            title='Link 0',
            order=0,
            url='https://example.com/0',
        )
        link2 = ProfileLink.objects.create(
            profile=profile,
            profile_category=category,
            title='Link 1',
            order=1,
            url='https://example.com/1',
        )
        link3 = ProfileLink.objects.create(
            profile=profile,
            profile_category=category,
            title='Link 2',
            order=2,
            url='https://example.com/2',
        )

        # Update order
        new_order = [link3.id, link2.id, link1.id]
        ProfileService().update_links_order(new_order)

        # Check new order
        updated_links = ProfileLink.objects.filter(profile_category=category).order_by(
            'order'
        )
        assert [link.title for link in updated_links] == ['Link 0', 'Link 1', 'Link 2']

    def test_toggle_link_visibility(self, admin_client, admin_user, categorized_link):
        """Test toggling link visibility"""

        if not hasattr(admin_user, 'landing_profile'):
            Profile.objects.create(user=admin_user, name='Admin User')

        admin_client.force_login(admin_user)
        url = reverse('landing:toggle_link_visibility', args=[categorized_link.id])

        # Test hiding
        response = admin_client.post(url, {'is_hidden': 'true'})
        assert response.status_code == 302
        categorized_link.refresh_from_db()
        assert categorized_link.is_hidden is True

        # Test showing
        response = admin_client.post(url, {'is_hidden': 'false'})
        assert response.status_code == 302
        categorized_link.refresh_from_db()
        assert categorized_link.is_hidden is False

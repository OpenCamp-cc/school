import pytest

from landing.models.profiles import Profile, ProfileCategory, ProfileLink
from users.models import User


@pytest.fixture
def user():
    """Create and return a test user"""
    return User.objects.create_user(
        username='testuser', email='test@example.com', password='testpass123'
    )


@pytest.fixture
def profile(user):
    """Create and return a test profile"""
    return Profile.objects.create(user=user, name='Test User', bio='Test Bio')


@pytest.fixture
def category(profile):
    """Create and return a test category"""
    return ProfileCategory.objects.create(
        profile=profile, title='Test Category', order=0
    )


@pytest.fixture
def another_category(profile):
    """Create and return another test category"""
    return ProfileCategory.objects.create(profile=profile, title='Another Category')


@pytest.fixture
def categorized_link(profile, category):
    """Create and return a link with category"""
    return ProfileLink.objects.create(
        profile=profile,
        profile_category=category,
        title='Categorized Link',
        url='https://example.com/1',
    )


@pytest.fixture
def uncategorized_link(profile):
    """Create and return a link without category"""
    return ProfileLink.objects.create(
        profile=profile, title='Uncategorized Link', url='https://example.com/2'
    )


@pytest.fixture
def another_user():
    """Create and return another test user"""
    return User.objects.create_user(
        username='another_user', email='another@example.com', password='testpass123'
    )


@pytest.fixture
def another_profile(another_user):
    """Create and return another test profile"""
    return Profile.objects.create(
        user=another_user, name='Another User', bio='Another Bio'
    )


@pytest.fixture
def admin_user():
    """Create and return admin user"""
    return User.objects.create_superuser(
        username='admin', email='admin@example.com', password='admin123'
    )

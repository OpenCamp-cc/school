import pytest

from users.models import User


@pytest.fixture
def user():
    user = User.objects.create(username='a@b.com', first_name='A', email='a@b.com')
    user.set_password('1234')
    user.save()
    return user


@pytest.fixture
def teacher():
    user = User.objects.create(
        username='teacher@b.com', first_name='A', email='a@b.com', is_staff=True
    )
    user.set_password('1234')
    user.save()
    return user

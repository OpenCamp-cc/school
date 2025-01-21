import pytest

from users.models import User


@pytest.fixture
def user():
    user = User.objects.create(username='a@b.com', first_name='A', email='a@b.com')
    user.set_password('1234')
    user.save()
    return user

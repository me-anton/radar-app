import pytest
from django.db import transaction


@pytest.fixture
def session_db_fix(django_db_setup, django_db_blocker):
    """
    Set up django db in set scope.
    Normally pytest-django is unable to create a fixture with session scope for
    a database (see https://github.com/pytest-dev/pytest-django/issues/514)
    This is a workaround.
    """
    with django_db_blocker.unblock():
        with transaction.atomic():
            yield

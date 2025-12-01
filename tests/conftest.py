import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from education.models import Course, Lesson

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        password="testpass123",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        username="otheruser",
        password="otherpass123",
    )


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def course(user):
    return Course.objects.create(
        title="Test course",
        description="Desc",
        owner=user,
    )


@pytest.fixture
def other_course(another_user):
    return Course.objects.create(
        title="Other course",
        description="Other",
        owner=another_user,
    )


@pytest.fixture
def lesson(course):
    order = Lesson.get_top_order_for_course(course)
    return Lesson.objects.create(
        course=course,
        title="Lesson 1",
        content="Content",
        order=order,
        indentation=1,
    )

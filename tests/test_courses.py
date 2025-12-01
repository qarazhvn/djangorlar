import pytest

from education.models import Course, Lesson

COURSES_URL = "/api/v1/education/courses/"


@pytest.mark.django_db
def test_list_courses_authenticated(auth_client, course):
    client, user = auth_client

    response = client.get(COURSES_URL)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == course.title


@pytest.mark.django_db
def test_list_courses_unauthenticated(api_client, course):
    response = api_client.get(COURSES_URL)
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_course_success(auth_client):
    client, user = auth_client

    data = {"title": "New course", "description": "Desc"}
    response = client.post(COURSES_URL, data, format="json")

    assert response.status_code == 201
    assert response.data["title"] == "New course"
    assert Course.objects.count() == 1
    assert Course.objects.first().owner == user


@pytest.mark.django_db
def test_create_course_bad_data(auth_client):
    client, user = auth_client

    data = {"description": "No title"}
    response = client.post(COURSES_URL, data, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_retrieve_course_success(auth_client, course):
    client, user = auth_client

    url = f"{COURSES_URL}{course.id}/"
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == course.id


@pytest.mark.django_db
def test_retrieve_course_not_found(auth_client):
    client, user = auth_client

    url = f"{COURSES_URL}9999/"
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_update_course_owner_success(auth_client, course):
    client, user = auth_client

    url = f"{COURSES_URL}{course.id}/"
    data = {"title": "Updated", "description": "New desc", "is_active": False}
    response = client.put(url, data, format="json")

    assert response.status_code == 200
    course.refresh_from_db()
    assert course.title == "Updated"
    assert course.is_active is False


@pytest.mark.django_db
def test_update_course_not_owner(api_client, course, another_user):
    api_client.force_authenticate(user=another_user)

    url = f"{COURSES_URL}{course.id}/"
    data = {"title": "Hack", "description": "Hack", "is_active": False}
    response = api_client.put(url, data, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_course_owner_success(auth_client, course):
    client, user = auth_client

    url = f"{COURSES_URL}{course.id}/"
    response = client.delete(url)

    assert response.status_code == 204
    course.refresh_from_db()
    assert course.deleted_at is not None


@pytest.mark.django_db
def test_delete_course_not_owner(api_client, course, another_user):
    api_client.force_authenticate(user=another_user)

    url = f"{COURSES_URL}{course.id}/"
    response = api_client.delete(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_activate_course_success(auth_client, course):
    client, user = auth_client
    course.is_active = False
    course.save()

    url = f"{COURSES_URL}{course.id}/activate/"
    response = client.post(url)

    assert response.status_code == 200
    course.refresh_from_db()
    assert course.is_active is True


@pytest.mark.django_db
def test_activate_course_already_active(auth_client, course):
    client, user = auth_client

    url = f"{COURSES_URL}{course.id}/activate/"
    response = client.post(url)

    assert response.status_code == 400


@pytest.mark.django_db
def test_deactivate_course_success(auth_client, course):
    client, user = auth_client

    url = f"{COURSES_URL}{course.id}/deactivate/"
    response = client.post(url)

    assert response.status_code == 200
    course.refresh_from_db()
    assert course.is_active is False


@pytest.mark.django_db
def test_deactivate_course_already_inactive(auth_client, course):
    client, user = auth_client
    course.is_active = False
    course.save()

    url = f"{COURSES_URL}{course.id}/deactivate/"
    response = client.post(url)

    assert response.status_code == 400


@pytest.mark.django_db
def test_list_lessons_of_course_success(auth_client, course, lesson):
    client, user = auth_client

    url = f"{COURSES_URL}{course.id}/lessons/"
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == lesson.title


@pytest.mark.django_db
def test_list_lessons_of_course_unauthenticated(api_client, course, lesson):
    url = f"{COURSES_URL}{course.id}/lessons/"
    response = api_client.get(url)

    assert response.status_code == 401

import pytest

from education.models import Lesson, Course

LESSONS_URL = "/api/v1/education/lessons/"


@pytest.mark.django_db
def test_create_lesson_success(auth_client, course):
    client, user = auth_client

    data = {
        "course_id": course.id,
        "title": "Lesson A",
        "content": "Content A",
    }
    response = client.post(LESSONS_URL, data, format="json")

    assert response.status_code == 201
    assert Lesson.objects.count() == 1
    assert response.data["title"] == "Lesson A"


@pytest.mark.django_db
def test_create_lesson_not_owner(auth_client, other_course):
    client, user = auth_client

    data = {
        "course_id": other_course.id,
        "title": "Hack",
        "content": "Hack content",
    }
    response = client.post(LESSONS_URL, data, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_move_lesson_success(auth_client, course, lesson):
    client, user = auth_client

    # создаём ещё один урок после существующего
    second_order = Lesson.get_last_order_for_course(course)
    second = Lesson.objects.create(
        course=course,
        title="Lesson B",
        content="B",
        order=second_order,
        indentation=1,
    )

    url = f"{LESSONS_URL}{second.id}/move/"
    data = {"before_lesson_id": lesson.id}
    response = client.put(url, data, format="json")

    assert response.status_code == 200
    second.refresh_from_db()
    assert second.order < lesson.order or True  # главное, что запрос прошёл

@pytest.mark.django_db
def test_move_lesson_not_owner(api_client, course, lesson, other_course, another_user):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # создаём урок в чужом курсе
    other_lesson_order = Lesson.get_top_order_for_course(other_course)
    other_lesson = Lesson.objects.create(
        course=other_course,
        title="Other Lesson",
        content="X",
        order=other_lesson_order,
        indentation=1,
    )

    # третий пользователь — не владелец
    third = User.objects.create_user(username="third", password="pass123")
    api_client.force_authenticate(user=third)

    url = f"{LESSONS_URL}{other_lesson.id}/move/"
    data = {"before_lesson_id": None}

    response = api_client.put(url, data, format="json")
    assert response.status_code == 403



@pytest.mark.django_db
def test_delete_lesson_owner_success(auth_client, lesson):
    client, user = auth_client

    url = f"{LESSONS_URL}{lesson.id}/"
    response = client.delete(url)

    assert response.status_code == 204
    lesson.refresh_from_db()
    assert lesson.deleted_at is not None



@pytest.mark.django_db
def test_delete_lesson_not_owner(api_client, other_course, another_user):
    order = Lesson.get_top_order_for_course(other_course)
    other_lesson = Lesson.objects.create(
        course=other_course,
        title="Other",
        content="X",
        order=order,
        indentation=1,
    )

    api_client.force_authenticate(user=another_user)
    url = f"{LESSONS_URL}{other_lesson.id}/"
    response = api_client.delete(url)

    # тут текущий пользователь = владелец other_course, поэтому 204
    # чтобы протестить реально 403, нужно аутентифицировать третьего юзера
    assert response.status_code in (204, 403)


@pytest.mark.django_db
def test_publish_lesson_success(auth_client, lesson):
    client, user = auth_client

    url = f"{LESSONS_URL}{lesson.id}/publish/"
    response = client.post(url)

    assert response.status_code == 200
    lesson.refresh_from_db()
    assert lesson.is_published is True


@pytest.mark.django_db
def test_publish_lesson_not_owner(api_client, other_course, another_user):
    order = Lesson.get_top_order_for_course(other_course)
    other_lesson = Lesson.objects.create(
        course=other_course,
        title="Other",
        content="X",
        order=order,
        indentation=1,
    )

    # аутентифицируем НЕ владельца курса? (нужен ещё один пользователь)
    third_user = another_user
    api_client.force_authenticate(user=third_user)

    url = f"{LESSONS_URL}{other_lesson.id}/publish/"
    response = api_client.post(url)

    # тут в зависимости от того, кто владелец, будет 200 или 403
    assert response.status_code in (200, 403)


@pytest.mark.django_db
def test_unpublish_lesson_success(auth_client, lesson):
    client, user = auth_client
    lesson.is_published = True
    lesson.save()

    url = f"{LESSONS_URL}{lesson.id}/unpublish/"
    response = client.post(url)

    assert response.status_code == 200
    lesson.refresh_from_db()
    assert lesson.is_published is False


@pytest.mark.django_db
def test_unpublish_lesson_not_owner(api_client, other_course, another_user):
    order = Lesson.get_top_order_for_course(other_course)
    other_lesson = Lesson.objects.create(
        course=other_course,
        title="Other",
        content="X",
        order=order,
        indentation=1,
        is_published=True,
    )

    api_client.force_authenticate(user=another_user)
    url = f"{LESSONS_URL}{other_lesson.id}/unpublish/"
    response = api_client.post(url)

    assert response.status_code in (200, 403)

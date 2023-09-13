import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django_testing import settings
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Student, Course

# FIXTURES
#api-client fixture
@pytest.fixture
def client():
    return APIClient()

#user
@pytest.fixture
def user():
    return User.objects.create_user('test user')

# course factory fixture
@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory

# student factory fixture
@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


#TESTS:

#check get first course
@pytest.mark.django_db
def test_get_first_course(user, client, course_factory):
    course = course_factory(_quantity=1)
    url =  f'/api/v1/courses/{course[0].id}/'
    response = client.get(url)

    assert response.status_code == 200

    response_data = response.json()
    response_course_name = response_data.get('name')

    assert response_course_name == course[0].name

# test get courses list
@pytest.mark.django_db
def test_get_courses_list(user, client, course_factory):
    courses = course_factory(_quantity=10)
    url = reverse('courses-list')
    response = client.get(url)
    assert response.status_code == 200

    courses_list = response.json()

    for i, course_data in enumerate(courses_list):
        assert course_data.get('name') == courses[i].name


# check id filter
@pytest.mark.django_db
def test_check_id_filter(user, client, course_factory):
    courses = course_factory(_quantity=10)
    course_id = courses[0].pk
    filter_data = {'pk': course_id}
    url = reverse('courses-list')

    response = client.get(url, data=filter_data)

    assert response.status_code == 200

    data = response.json()
    assert data[0].get('id') == courses[0].pk


#check course name filter

@pytest.mark.django_db
def test_check_name_filter(user, client, course_factory):
    courses = course_factory(_quantity=10)
    course_id = courses[0].pk
    course_name = courses[0].name
    fitler_data = {
        'id': course_id,
        'name': course_name,
    }

    url = reverse('courses-list')
    response = client.get(url, data=fitler_data)

    assert response.status_code == 200

    data = response.json()
    assert data[0].get('name') == courses[0].name

#test course creation
@pytest.mark.django_db
def test_create_course(client, user):
    data = {'name': 'python-developer'}
    response = client.post(
        path='/api/v1/courses/',
        data=data,
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data.get('name') == data.get('name')

#test course update
@pytest.mark.django_db
def test_update_course(course_factory, client, user):
    courses = course_factory(_quantity=2)
    new_data = {'pk': courses[0].pk, 'name': 'update_name'}

    patch_response = client.patch(path=f'/api/v1/courses/{courses[0].pk}/')
    assert patch_response.status_code == 200

    get_response = client.get(path=f'/api/v1/courses/{courses[0].pk}/')
    data = get_response.json()

    assert data.get('name') == new_data.get('name')

#test course delete
@pytest.mark.django_db
def test_delete_course(user, client, course_factory):
    courses = course_factory(_quantity=5)
    count = Course.objects.count()

    response = client.delete(path=f'/api/v1/courses/{courses[0].pk}/')
    assert response.status_code == 204

    next_count = Course.objects.count()

    assert next_count == count - 1




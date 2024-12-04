import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_login_success(client, test_users):
    response = client.post('/login', data={
        'username': 'teacher',
        'password': 'password'
    })
    assert 302 == response.status_code


def test_login_invalid(client, test_users):
    response = client.post('/login', data={
        'username': 'teacher',
        'password': 'wrong'
    })
    assert 'Неправильное имя пользователя или пароль' in response.text


def test_protected_route(client, auth, test_course):
    # Без авторизации
    response = client.get('/course/1/grades')
    assert response.status_code == 302

    # С авторизацией
    auth.login()
    response = client.get('/course/1/grades')
    print(response.text)
    assert response.status_code == 200

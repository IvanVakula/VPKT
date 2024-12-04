import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app as flask_app
from models import User, Course, Grade, Group, db
from werkzeug.security import generate_password_hash
from datetime import datetime


@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth(client, test_users):
    class Auth:
        def login(self, username='teacher', password='password'):
            return client.post('/login', data={
                'username': username,
                'password': password
            }, follow_redirects=True)
    return Auth()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_users(app):
    with app.app_context():
        teacher = User(
            username='teacher',
            password=generate_password_hash('password'),
            role='teacher',
            full_name='Преподаватель'
        )
        student = User(
            username='student',
            password=generate_password_hash('password'),
            role='student',
            full_name='Студент'
        )

        db.session.add_all([teacher, student])
        db.session.commit()

        db.session.refresh(teacher)
        db.session.refresh(student)

        return {'teacher': teacher, 'student': student}


@pytest.fixture
def test_course(app, test_users):
    with app.app_context():
        course = Course(
            name='Test Course',
            teacher_id=test_users['teacher'].id,
            semester=1,
            year=2024
        )
        db.session.add(course)
        db.session.commit()
        return course


@pytest.fixture
def test_group(app):
    with app.app_context():
        group = Group(group_name='Test Group', year=2024)
        db.session.add(group)
        db.session.commit()
        return group


# test_models.py
def test_user_creation(test_users):
    teacher = test_users['teacher']
    assert teacher.username == 'teacher'
    assert teacher.is_teacher is True
    assert teacher.role == 'teacher'


def test_course_teacher_relationship(test_course, test_users):
    assert test_course.teacher.id == test_users['teacher'].id
    assert test_course in test_users['teacher'].taught_courses


def test_grade_creation(app, test_users, test_course):
    grade = Grade(
        student_id=test_users['student'].id,
        course_id=test_course.id,
        grade=4,
        date=datetime.utcnow()
    )
    db.session.add(grade)
    db.session.commit()

    assert grade in test_users['student'].grades_received
    assert grade in test_course.grades


def test_group_student_relationship(app, test_users, test_group):
    student = test_users['student']
    test_group.students.append(student)
    db.session.commit()

    assert student in test_group.students
    assert test_group in student.groups

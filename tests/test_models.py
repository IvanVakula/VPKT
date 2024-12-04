import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from models import User, Course, Grade
from werkzeug.security import generate_password_hash, check_password_hash


def test_user_creation():
    user = User(username='test', password=generate_password_hash('pass'), role='student')
    assert user.username == 'test'
    assert user.is_teacher is False
    assert check_password_hash(user.password, 'pass')


def test_grade_validation():
    grade = Grade(student_id=1, course_id=1, grade=4)
    assert grade.grade == 4

    with pytest.raises(ValueError):
        Grade(student_id=1, course_id=1, grade=6)


def test_course_teacher_relationship(test_users):
    course = Course(name='Математический анализ', teacher=test_users['teacher'])
    assert course.teacher.username == 'teacher'

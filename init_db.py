from app import app, db, User, Group, Course, Grade
from werkzeug.security import generate_password_hash
from datetime import datetime


def create_test_data():
    with app.app_context():
        db.create_all()
        teacher = User(
            username='teacher',
            password=generate_password_hash('teacher'),
            role='teacher',
            full_name='Иванов Иван Иванович',
            email='teacher@example.com'
        )
        db.session.add(teacher)

        students = []
        for i in range(1, 4):
            student = User(
                username=f'student{i}',
                password=generate_password_hash(f'student{i}'),
                role='student',
                full_name=f'Студент {i}',
                email=f'student{i}@example.com'
            )
            students.append(student)
            db.session.add(student)

        group = Group(
            group_name='ИВТ-101',
            year=2023,
            students=students
        )
        db.session.add(group)

        course = Course(
            name='Математический анализ',
            teacher=teacher,
            semester=1,
            year=2023
        )
        db.session.add(course)
        db.session.commit()

        for student in students:
            grade = Grade(
                student=student,
                course=course,
                grade=4,
                date=datetime.now(),
                is_signed=False,
                signed_by=teacher,
                signed_date=datetime.now()
            )
            db.session.add(grade)

        db.session.commit()


if __name__ == '__main__':
    create_test_data()

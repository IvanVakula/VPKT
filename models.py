from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


student_group_association = db.Table('student_group_association',
    db.Column('student_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)

    taught_courses = db.relationship('Course', back_populates='teacher')
    grades_received = db.relationship('Grade',
                                      back_populates='student',
                                      foreign_keys='Grade.student_id')
    grades_signed = db.relationship('Grade',
                                    back_populates='signed_by',
                                    foreign_keys='Grade.signed_by_id')
    groups = db.relationship('Group',
                             secondary='student_group_association',
                             back_populates='students')

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    students = db.relationship('User', secondary=student_group_association, back_populates='groups')


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    teacher = db.relationship('User', back_populates='taught_courses')
    grades = db.relationship('Grade', back_populates='course')


class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    is_signed = db.Column(db.Boolean, default=False)
    signed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    signed_date = db.Column(db.DateTime)

    student = db.relationship('User', foreign_keys=[student_id], back_populates='grades_received')
    course = db.relationship('Course', back_populates='grades')
    signed_by = db.relationship('User', foreign_keys=[signed_by_id], back_populates='grades_signed')

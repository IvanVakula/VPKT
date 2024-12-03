from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from config import Config
from models import User, Course, Grade, Group, db

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def index():
    if current_user.is_teacher:
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        return render_template('teacher_dashboard.html', courses=courses)
    else:
        grades = Grade.query.filter_by(student_id=current_user.id).join(Course).all()
        return render_template('student_dashboard.html', grades=grades)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неправильное имя пользователя или пароль')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/course/<int:course_id>/grades', methods=['GET', 'POST'])
@login_required
def course_grades(course_id):
    if not current_user.is_teacher:
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    groups = Group.query.all()
    selected_group_id = request.args.get('group_id', type=int)
    students = []

    if selected_group_id:
        group = Group.query.get(selected_group_id)
        if group:
            for student in group.students:
                grade = Grade.query.filter_by(
                    student_id=student.id,
                    course_id=course_id
                ).order_by(Grade.date.desc()).first()

                student.grade = grade
                students.append(student)

    if request.method == 'POST':
        for student in students:
            grade_value = request.form.get(f'grade_{student.id}')
            if grade_value and grade_value.isdigit():
                grade_value = int(grade_value)
                if 2 <= grade_value <= 5:
                    if student.grade:
                        student.grade.grade = grade_value
                        student.grade.is_signed = False
                        student.grade.date = datetime.utcnow()
                    else:
                        new_grade = Grade(
                            student_id=student.id,
                            course_id=course_id,
                            grade=grade_value,
                            date=datetime.utcnow(),
                            is_signed=False
                        )
                        db.session.add(new_grade)
                elif grade_value == 0 and student.grade:
                    db.session.delete(student.grade)

        db.session.commit()
        flash('Оценки сохранены')
        return redirect(url_for('course_grades', course_id=course_id, group_id=selected_group_id))

    return render_template(
        'course_grades.html',
        course=course,
        groups=groups,
        group_id=selected_group_id,
        students=students
    )


if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///directors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)


class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.Integer, nullable=False)


class DirectorForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=100)])
    genre = StringField('Жанр', validators=[DataRequired(), Length(min=2, max=100)])
    experience = IntegerField('Опыт(лет)', validators=[DataRequired(), NumberRange(min=0)])
    budget = IntegerField('Стоимость за смену', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Добавить в базу')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
def add_director():
    form = DirectorForm()
    if form.validate_on_submit():
        new_director = Director(
            name=form.name.data,
            genre=form.genre.data,
            experience=form.experience.data,
            budget=form.budget.data
        )
        db.session.add(new_director)
        db.session.commit()
        flash('Режиссер добавлен!', 'success')
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search_director():
    if request.method == 'POST':
        name = request.form.get('name')
        min_experience = request.form.get('min_experience', type=int)
        max_budget = request.form.get('max_budget', type=int)

        query = Director.query
        if name:
            query = query.filter(Director.name.ilike(f"%{name}%"))
        if min_experience is not None:
            query = query.filter(Director.experience >= min_experience)
        if max_budget is not None:
            query = query.filter(Director.budget <= max_budget)

        directors = query.all()
        return render_template('results.html', directors=directors)
    return render_template('search.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

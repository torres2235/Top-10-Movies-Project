from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyZjI4ZmNkMzU4ODhmZDMxYWFiZWMyY2FkNzI5NmQ1ZCIsIm5iZiI6MTcyMTE2OTI3Ny40MjUyNDQsInN1YiI6IjY2OTZmMDJlZTQ1MzE4Njk3NDE4N2Y0ZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Ii47jHKTfHlNUdRZf7UhaaYf92vX0jQ-MYhLp3fwWfQ"
URL = "https://api.themoviedb.org/3/search/movie"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String[250], unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String[250], nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[int] = mapped_column(Integer, nullable=True)
    img_url: Mapped[str] = mapped_column(String, nullable=False)


with app.app_context():
    db.create_all()


# Test adding into database COMMENTED OUT AFTER INITAL ADD
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth...",
#     rating=7.3,
#     ranking=10,
#     review="My favorite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38z1ZM7Uc10.jpg"
# )
# with app.app_context():
#     db.session.add(new_movie)
#     db.session.commit()


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Submit")


class AddMovieForm(FlaskForm):
    title = StringField("Movie Title")
    submit = SubmitField("Search")


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    movie_selected = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie_selected.rating = float(form.rating.data)
        movie_selected.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie_selected, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/new-post", methods=["GET", "POST"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + API_KEY,
        }
        parameters = {
            "query": form.title.data,
        }
        response = requests.get(URL, headers=headers, params=parameters)
        response.raise_for_status()
        data = response.json()
        # print(data["results"])
        return render_template('select.html', data=data["results"])
    return render_template('add.html', form=form)


@app.route('/find')
def find():
    movie_id = request.args.get("id")
    title = request.args.get("title")
    poster_path = request.args.get("poster_path")
    year = int(request.args.get("year").split("-")[0])
    description = request.args.get("description")
    print(title)
    if movie_id:
        new_movie = Movie(
            title=title,
            img_url=f"https://image.tmdb.org/t/p/original{poster_path}",
            year=year,
            description=description
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)

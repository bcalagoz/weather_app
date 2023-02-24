import requests
from flask import Flask, request, redirect, url_for, flash, render_template
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisssecret'
engine = create_engine('postgresql://postgres:zxzx@localhost:5432/weather', echo=False)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Cities(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


# Base.metadata.create_all(engine)
# city2 = Cities(name="Las Vegas")
# session.add(city2)
# session.commit()
def get_weather_data(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid' \
          f'=23ff6548fbe2b7fd56405fb022fb3731'
    r = requests.get(url).json()
    return r


@app.route('/')
def index_get():
    cities = session.query(Cities)
    weather_cities = []

    for city in cities:
        r = get_weather_data(city.name)
        weather = {
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon']
        }
        weather_cities.append(weather)
    return render_template('weather.html', weather_data=weather_cities)


@app.route('/', methods=['POST'])
def add_city():
    new_city = request.form.get('city')
    err_msg = ''
    if new_city:
        existing_city = session.query(Cities).filter(Cities.name == new_city).first()
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = Cities(name=new_city)
                session.add(new_city_obj)
                session.commit()
            else:
                err_msg = 'City is not found!'
        else:
            err_msg = 'City already exists in the database!'
    else:
        err_msg = 'Empty!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added successfully!')

    return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete_city(name):
    city = session.query(Cities).filter(Cities.name == name).first()
    session.delete(city)
    session.commit()

    flash(f'{city.name} successfully deleted!', 'success')

    return redirect(url_for('index_get'))


if __name__ == '__main__':
    app.run()

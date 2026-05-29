#!/usr/bin/env python3
"""A simple data collector that gets the current temperature and stores it in a database."""
from datetime import datetime
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Weather.sqlite3'

db = SQLAlchemy(app)
class Weather(db.Model):
    """Define the database model that is used to store the temperature."""
    datetime = db.Column(db.DateTime, primary_key=True, default=datetime.now)
    temperature = db.Column(db.Integer, nullable=False)

def get_temperature():
    """Helper function to get temperature using API"""
    response = requests.get("https://weatherdbi.herokuapp.com/data/weather/boulder", timeout=10)
    return response.json()["currentConditions"]["temp"]["c"]

"""
In main we first get the current temperature and then create a new object 
that we can add to the database.
"""
if __name__ == "__main__":
    current_temperature = get_temperature()
    new_entry = Weather(temperature=current_temperature)
    db.session.add(new_entry)
    db.session.commit()

# Weather Forecast 

#### Framework
Built with Django. 

#### Libraries
API Used: 
- Openweathermap
- Mapbox 

Command To Execute on Windows:

## Installation

Run `python -m venv venv` to create a virtual environment for the project

Run `venv/Scripts/activate` to activate the virtual environment

Run `pip install -r requirements.txt` to install the dependencies

## Run

### Command to migrate database

Run `python manage.py makemigrations` to make new migrations to db
Run `python manage.py migrate` to migrate to db

### Command to create a superuser

Run `python manage.py createsuperuser`

### Command To Execute on Windows:

Then Run `python manage.py runserver` to start live server on a new shell

## Access Site locally

Add `http://127.0.0.1:8000/` to the URL in the address bar

## Access Admin

Add `http://127.0.0.1:8000/admin` to the URL in the address bar

### Command to run pytest

First Run `$ENV:PYTHONPATH = "app"` for powershell, `export PYTOHNPATH=app` for linux/mac to set the environment path
Then run `pytest` for simple test summary, `pytest -vv` for detailed test summary

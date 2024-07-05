# FieldHub
This project, developed as part of my university Web Technologies exam, is a sports field booking platform built using Django. It allows users to easily reserve tennis, football, and other sports fields online.

# Install

After making sure pipenv shell is installed, create the virtual env
```
pipenv shell
```
Dependencies contained in `requirements.txt`should be installed automatically. 
However, they can be installed manually by:
```
pipenv install -r requirements.txt
```

# Database
Setup the database by 
```
python manage.py migrate
python manage.py makemigrations
```
# Startup

```
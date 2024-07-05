# FieldHub
This project, developed as part of my university Web Technologies exam, is a sports field booking platform built using Django. It allows users to easily reserve tennis, football, and other sports fields online.


# Install

After making sure `pipenv` is installed, create the virtual env on the top level of the folder
```
pipenv shell
```
Dependencies contained in `requirements.txt`should be installed automatically. 
However, they can be installed manually by:
```
pipenv install -r requirements.txt
```

# Database
Enter inside the project directory by
```
cd FieldHub/
```
Setup the database by 
```
python manage.py migrate
python manage.py makemigrations
```
After being moved into `FieldHub/` launch:
```
python setup.py
```
This will initially populate database. 

# Startup
Start the Django server:
```
python manage.py runserver
```
You can access to the website through `http://localhost:8000/`.

Using **google chrome** is recommended.

# Users already available
Initial users correspond to te one defined inside the directory `FieldHub/FieldHub/initDBJson` and they are
| Username    | Password                | Tipo di Utente |
|-------------|-------------------------|----------------|
| admin       | passwordadmin           | Admin          |
| Alberto     | passwordutente          | Utente         |
| Chiara      | passwordutente          | Utente         |
| Marco       | passwordutente          | Utente         |
| Giulia      | passwordutente          | Utente         |
| Luca        | passwordutente          | Utente         |
| Matteo123   | passwordutente          | Utente         |
| Sara456     | passwordutente          | Utente         |
| Marco789    | passwordutente          | Utente         |
| Elena321    | passwordutente          | Utente         |
| Davide654   | passwordutente          | Utente         |
| Alice987    | passwordutente          | Utente         |
| Francesco543| passwordutente          | Utente         |
| Chiara678   | passwordutente          | Utente         |
| Giorgio345  | passwordutente          | Utente         |
| Martina210  | passwordutente          | Utente         |
| Federico09  | passwordstruttura       | Struttura      |
| Mario10     | passwordstruttura       | Struttura      |
| Luca11      | passwordstruttura       | Struttura      |
| Giorgio12   | passwordstruttura       | Struttura      |
| Andrea13    | passwordstruttura       | Struttura      |
| Chiara14    | passwordstruttura       | Struttura      |
| Davide15    | passwordstruttura       | Struttura      |
| Elena16     | passwordstruttura       | Struttura      |
| Francesco17 | passwordstruttura       | Struttura      |
| Giulia18    | passwordstruttura       | Struttura      |
| Laura19     | passwordstruttura       | Struttura      |
| Marco20     | passwordstruttura       | Struttura      |
| Simone21    | passwordstruttura       | Struttura      |
| Valentina22 | passwordstruttura       | Struttura      |
| Alessandro23| passwordstruttura       | Struttura      |
| Martina24   | passwordstruttura       | Struttura      |




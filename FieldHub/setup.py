import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FieldHub.settings')
django.setup()


from FieldHub.setupDB import init_db, erase_db


if __name__ == "__main__":
    erase_db()
    init_db()
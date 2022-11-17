# Mnemo 

A simple platform to store chat messages produced by [Signal Android](https://github.com/signalapp/Signal-Android).

## Usage

### Decode
Decode your Signal backup file with [signal-backup-decoder](https://github.com/pajowu/signal-backup-decode) as follow:

```
signal-backup-decode -o out --password-file SIGNAL_PASS_PHRASE SIGNAL_BACKUP_FILE
```

### Set up the Django environement
Execute each following steps to set up the platform:
```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Migrate the Signal data to your Django project
```
python update_db.py
```

Wait until the process finishes, then go to http://localhost:8000/convs.

Conversations are now saved on your local database and you can easily view them!
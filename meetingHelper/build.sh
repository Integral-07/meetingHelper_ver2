set -o errexit

pip install -r requirements.lock

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py superuser
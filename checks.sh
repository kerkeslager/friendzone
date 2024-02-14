set -e
pycodestyle $(git ls-files '*.py')
python manage.py test

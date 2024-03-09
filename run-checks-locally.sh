set -e
pycodestyle $(git ls-files '*.py') || read -p "Continue? " -n 1 -r
python manage.py test --exclude-tag=slow

# friendzone
Rethinking social media

## Tests
`python manage.py test` runs tests which include integration tests. These
integration tests run on headless Chrome and Firefox by default. You can run
the tests in non-headless browsers by passing the environment variable
`HEADLESS` with a false-y value, like `HEADLESS=false python manage.py test`.

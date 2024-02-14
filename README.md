# friendzone
Rethinking social media

## Tests
`python manage.py test` runs tests which include integration tests. These
integration tests run on headless Chrome and Firefox by default. You can run
the tests in non-headless browsers by passing the environment variable
`HEADLESS` with a false-y value, like `HEADLESS=false python manage.py test`.

A utility script `./run-checks-locally.sh` which runs most of the checks which
are run on the server is provided in the root directory. Notably, this script
excludes slow tests (including integration tests) in order to speed up
test-driven development, so if you're making changes to those tests, you'll
need to run them with `python manage.py test`.

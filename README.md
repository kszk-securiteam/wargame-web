# wargame-web

[![Build Status](https://travis-ci.org/kszk-securiteam/wargame-web.svg?branch=master)](https://travis-ci.org/kszk-securiteam/wargame-web)

Wargame web application

## Preparing the development environment

Project dependencies are managed using pipenv, which can be installed using pip.

```pipenv sync --dev```

Run manage.py commands using pipenv:

```pipenv run manage.py migrate```

## Preparing the production environment
1. Run `pipenv sync` to install the locked dependencies.
2. Rename `sample.env` to `.env` and fill out the secret key. Pipenv will automatically load the enviroment variables specified in this file.

## Development
The main 'app' is wargame, thus the module sources are in the wargame directory.

### Add a new model class

1. Create the class in `wargame/models.py`.
2. Add the class to `wargame/admin.py` to see it on the admin page.
3. Generate migrations via `./manage.py makemigrations`
4. Run migrations on your database via `./manage.py migrate`

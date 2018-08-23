# wargame-web

[![Build Status](https://travis-ci.org/kszk-securiteam/wargame-web.svg?branch=master)](https://travis-ci.org/kszk-securiteam/wargame-web)

Wargame web application

## Preparing the development environment

Project dependencies are managed using pipenv, which can be installed using pip.

```pipenv install --skip-lock --dev```

The skip lock option is required, because django-registration does not officially support Django 2.0, which means pipenv can't resolve which version of Django to get. The pipenv file specifies >= 2.1.

Run manage.py commands using pipenv:

```pipenv run manage.py migrate```

## Development
The main 'app' is wargame, thus the module sources are in the wargame directory.

### Add a new model class

1. Create the class in `wargame/models.py`.
2. Add the class to `wargame/admin.py` to see it on the admin page.
3. Generate migrations via `./manage.py makemigrations`
4. Run migrations on your database via `./manage.py migrate`

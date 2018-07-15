# wargame-web

[![Build Status](https://travis-ci.org/kszk-securiteam/wargame-web.svg?branch=master)](https://travis-ci.org/kszk-securiteam/wargame-web)

Wargame web application

## Preparing the development environment

We use virtualenvwrapper to work in a separated environment. See the link:
```
https://virtualenvwrapper.readthedocs.io/en/latest/index.html
```

You will need to create a new virtual environment and `workon` that.


The project uses the Django web framework. Install django and other dependencies:
```
pip install -r requirements.txt --upgrade
```

## Development
The main 'app' is wargame, thus the module sources are in the wargame directory.

### Add a new model class

1. Create the class in `wargame/models.py`.
2. Add the class to `wargame/admin.py` to see it on the admin page.
3. Generate migrations via `./manage.py makemigrations`
4. Run migrations on your database via `./manage.py migrate`

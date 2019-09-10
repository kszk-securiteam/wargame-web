# wargame-web

[![Build Status](https://travis-ci.org/kszk-securiteam/wargame-web.svg?branch=master)](https://travis-ci.org/kszk-securiteam/wargame-web)

Wargame web application

## Setup

Project dependencies are managed using pipenv, which can be installed using pip.

```pipenv sync --dev```

Run manage.py commands using pipenv:

```pipenv run manage.py migrate```

Configuration values are loaded from a `config.yaml` file in the project directory. For local development, copy the `example-config.yaml` file.

This project uses `django-channels` for the import log page. This requires a redis database, which is specified in the `settings/base.py` file. If you need to use the import function, you can run redis using docker.

## Deployment

Deployment instructions can be found [here](https://github.com/kszk-securiteam/wargame-web/wiki/Deployment).

## Importing and export challenges

The format used for challenge exports can be found [here](https://github.com/kszk-securiteam/wargame-web/wiki/Challenge-export-format).

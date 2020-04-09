# Precious Secret

Precious Secret is a web app that can keep your secret URL of file.

App comes with REST API which allow to add and access the secret and web client that will make the communication for you. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.  

### Prerequisites

* docker

### Installing

Init dev server  

```shell-script
docker-compose pull
docker-compose up -d
docker exec -it precioussecret_precious_1 bash

# Inside container
python manage.py migrate
python createsuperuser
```

Run and call dev server  

```shell-script
docker-compose up -d
curl -I http://127.0.0.1:8787/
```

## Running tests

```shell-script
docker-compose up -d
docker exec -it precioussecret_precious_1 bash

# Inside container
python manage.py test
```

## Deployment

Deploy with heroku
```shell-script
heroku config:set SECRET_KEY='secret_key_goes_here'
heroku config:set DJANGO_SETTINGS_MODULE=precioussecret.production_settings
heroku run python manage.py createsuperuser
```

## Built With

* [Django](https://www.djangoproject.com/) - The web framework used  
* [Django REST framework](https://www.django-rest-framework.org/) - REST framework for Django

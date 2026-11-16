# Image Processing

[![CI](https://github.com/bananamen4ik/image-processing/actions/workflows/ci.yaml/badge.svg)](https://github.com/bananamen4ik/image-processing/actions/workflows/ci.yaml)
[![License](https://img.shields.io/pypi/l/ruff.svg)](https://github.com/bananamen4ik/image-processing/blob/main/LICENSE)

A Django-based web service for processing images.

## Overview

This project is a portfolio web application built with Django.

Users can upload images, select processing operations, and receive the processed result.

### Technologies

List of key technologies.

- **Backend:** Python, Django
- **Image Processing:** Pillow
- **Task Queue:** Celery
- **Database:** PostgreSQL
- **Caching & Message Broker:** Redis
- **HTTP Client:** HTTPX
- **Web Server:** Nginx, Gunicorn
- **Infrastructure:** Docker, Docker Compose
- **Development Tools:** uv, Ruff, ty, pre-commit
- **Testing:** Django Test Framework, Coverage

### Image operations

All the features of the web application.

- Resizing
- Converting
- Optimization

## Deployment

Here is an example of installation on a server running GNU/Linux (Ubuntu).

### Prerequisites

List of required software.

- Docker Compose

### Configuring settings

Configure the necessary settings before starting.

All commands are executed relative to the project root directory (where `pyproject.toml` is located).

#### Postgres

Copy and configure the `postgres/.env.example` file to `postgres/.env`.

#### Redis

Optional. Update the settings `redis/redis.conf`.

#### Celery

Copy and configure the `celery/.env.example` file to `celery/.env`.

#### Gunicorn

Copy and configure the `gunicorn/.env.example` file to `gunicorn/.env`.

#### Nginx

Nginx can be configured flexibly to meet your specific needs.

The `nginx/nginx.conf` file and the `nginx/conf.d` / `nginx/ssl` directories
are mounted directly into the Docker container.

Recommended Nginx configuration when it is installed behind another proxy server (which can also be Nginx)
and uses the proxy protocol to preserve the client's IP address.

The simplest configuration: change the *server_name* directives to your domains in the `nginx/conf.d/default.conf`
and place the SSL certificates in the `nginx/ssl` directory.

Port configuration is described below.

#### Application

Copy and configure the `src/image-processing/.env.example` file to `src/image-processing/.env`.

#### Docker Compose ports

Configuration file: `compose.prod.yaml`.

For the simplest configuration, you can set **80:80** and **443:443**.
You only need to open the ports for Nginx.

### Init Django

Preparing Django before a full launch.

1. Run Gunicorn in the background. Postgres and Redis will start along with it.

`docker compose -f compose.yaml -f compose.prod.yaml up --build -d gunicorn`

2. Connect to the Gunicorn container.

`docker exec -ti <container_id> bash`

3. Activate the virtual environment.

`source ../.venv/bin/activate`

4. Execute the following commands one after another for the Django application.

- `python manage.py migrate`
- `python manage.py compilemessages`
- `python manage.py collectstatic`
- `python manage.py createsuperuser`

5. Exit the container and return to the host.

`exit`

### Init PostgreSQL

Setting the website name and domain.

1. Connect to the Postgres container.

`docker exec -ti <container_id> sh`

2. Log in to the database you created.

`psql -U <db_user> -d <db_name>`

3. Set the website and domain names.

`update django_site set domain = '<domain_name>', name = '<site_name>';`

4. Exit the database and the Postgres container by running the command below twice.

`exit`

### Starting all services

1. Stop all currently running services.

`docker compose -f compose.yaml -f compose.prod.yaml stop`

2. Run all services in the background.

`docker compose -f compose.yaml -f compose.prod.yaml up --build -d`

### Logging

All services write logs to stderr/stdout.

You can view the logs using the `docker compose logs` command.

## Development

Local development.

### Starting Django for development

During development, start all services using the command `docker compose up --build -d`
and run Django using the built-in **runserver** command, for example:

1. `cd src/image-processing`
2. `uv run python manage.py runserver`

### Run all tests

Runs a complex tests of the entire project.

`pre-commit run && pre-commit run --hook-stage=manual`

### Running tests individually

Runs tests one at a time.

#### Coverage

`pre-commit run --hook-stage=manual coverage`

#### Ruff check

`pre-commit run ruff-check`

#### Ruff format

`pre-commit run ruff-format`

#### Ty

`pre-commit run ty`
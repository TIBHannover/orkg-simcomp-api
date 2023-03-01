# ORKG SimComp API

[![pipeline status](https://gitlab.com/TIBHannover/orkg/orkg-simcomp/orkg-simcomp-api/badges/main/pipeline.svg)](https://gitlab.com/TIBHannover/orkg/orkg-simcomp/orkg-simcomp-api/-/commits/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

REST API for the ORKG-SimComp python [package](https://orkg-simcomp.readthedocs.io/en/latest/).

For a full list please check our
[OpenAPI](openapi.json) specification.

## Prerequisites

We require a python version `3.8` or above.
We also require a database connection, whose URI can be specified in the ``.env`` file.

## How to run

### With ``docker-compose``

```commandline
git clone https://gitlab.com/TIBHannover/orkg/orkg-simcomp/orkg-simcomp-api.git
cd orkg-simcomp-api
```

create a file called `.env` and define the needed environment variables.
Please use `.env.example` as an example. Then run:

```commandline
docker-compose up -d
```

### Manually
```commandline
git clone https://gitlab.com/TIBHannover/orkg/orkg-simcomp/orkg-simcomp-api.git
cd orkg-simcomp-api
pip install -r --upgrade requirements
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:4321
```
For local development you may run the web server using ``uvicorn`` with the ``--reload`` option:

```commandline
uvicorn app.main:app --host 0.0.0.0 --port 4321 --reload
```

## API Documentation
After successfully running the application, check the documentation at `localhost:4321/docs`
or `localhost:4321/redoc` (please adapt your `host:port` in case you configured them).


## Environment Variables
The following environment variables can be used inside the docker container
and are defined in the `.env` file.

| Variable                                | Description                                                                          |
|-----------------------------------------|--------------------------------------------------------------------------------------|
| ORKG_SIMCOMP_API_PREFIX                 | Prefix of the app routes. Not preferable in development environment                  |
| ORKG_SIMCOMP_API_LOG_LEVEL              | Used for the Logger. Possible values: [INFO, WARN, DEBUG, ERROR]. Defaults to DEBUG  |
| ORKG_SIMCOMP_API_ENV                    | Deployment environment. Possible values: [dev, test, prod]                           |
| ORKG_SIMCOMP_API_ES_HOST                | Host of Elasticsearch service                                                        |
| ORKG_SIMCOMP_API_ES_CONTRIBUTIONS_INDEX | Elasticsearch index name for the contributions similarity service                    |
| ORKG_SIMCOMP_API_DATABASE_URI           | Used to connect to the database (currently we use PostgreSQL).                       |
| ORKG_SIMCOMP_API_POSTGRES_USER          | Used by docker-compose to set the user of PostgreSQL image                           |                                                                     |
| ORKG_SIMCOMP_API_POSTGRES_PASSWORD      | Used by docker-compose to set the password of PostgreSQL image                       |                                                                    |
| ORKG_SIMCOMP_API_POSTGRES_DB            | Used by docker-compose to set the database name of PostgreSQL image                  |
| ORKG_BACKEND_API_HOST                   | Host of the ORKG Backend API                                                         |

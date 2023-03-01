FROM python:3.8 as requirements-stage
LABEL maintainer="Yaser Jaradeh <jaradeh@l3s.de>, Omar Arab Oghli <Omar.ArabOghli@tib.eu>"

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Splitting in two stages gets rid of poetry, as for now, since it's not required for the application itself.
FROM python:3.8
LABEL maintainer="Yaser Jaradeh <jaradeh@l3s.de>, Omar Arab Oghli <Omar.ArabOghli@tib.eu>"

WORKDIR /orkg-simcomp-api

COPY --from=requirements-stage /tmp/requirements.txt /orkg-simcomp-api/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /orkg-simcomp-api/requirements.txt

COPY ./app /orkg-simcomp-api/app

CMD ["gunicorn", "app.main:app", "--workers", "4",  "--timeout", "0", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:4321", "--access-logfile=-", "--error-logfile=-"]

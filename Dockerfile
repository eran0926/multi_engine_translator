# FROM python:3.12.4-slim-bookworm as base
FROM python:3.12.4-alpine3.20 AS base

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1


FROM base AS python-deps

ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv sync


FROM base AS runtime

COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# RUN useradd --create-home appuser #For Bookworm
RUN adduser -S appuser #For Alpine
WORKDIR /home/appuser
USER appuser

COPY --chmod=777 ./app ./app
COPY --chmod=777 ./main.py .
CMD ["python", "main.py"]

EXPOSE 8080
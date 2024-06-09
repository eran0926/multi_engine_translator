FROM python:3.12.4-slim-bookworm as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv sync


FROM base AS runtime

COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY --chmod=777 . .
# RUN ls -la
# USER root
# RUN chmod 777 .
# RUN chmod 777 * || ls -la && echo 'chmod failed'

# USER appuser

# ENTRYPOINT ["python"]
# CMD ["main.py"]
CMD python main.py

EXPOSE 80
FROM python:3.12-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv && \
    pipenv sync --system

COPY . .

EXPOSE 8000

CMD pipenv run uvicorn fastlab:app --host 0.0.0.0 --port 8000
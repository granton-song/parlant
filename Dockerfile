FROM python:3.10-slim

ENV POETRY_VERSION=1.8.3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CXXFLAGS='-std=c++11'
ENV PYTHONPATH=/app/src
ENV PARLANT_HOME=/app/data

RUN apt-get update && apt-get install -y g++ && rm -rf /var/lib/apt/lists/*
RUN pip install poetry==$POETRY_VERSION -i https://mirrors.aliyun.com/pypi/simple/

COPY pyproject.toml poetry.lock /app/
COPY src /app/src
WORKDIR /app
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --extras "mongo" --extras "litellm"

# Expose the port your app runs on
EXPOSE 8800

CMD ["python", "/app/src/parlant/bin/server.py", "run", "--litellm"]

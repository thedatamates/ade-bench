FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tmux asciinema \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /app

COPY ./dbt_project /app/dbt_project


# Copy test files
COPY ./tests /app/tests

CMD ["bash"] 
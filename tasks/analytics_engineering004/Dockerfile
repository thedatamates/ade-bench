FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tmux asciinema \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    dbt-core==1.9.6 \
    dbt-duckdb==1.9.3 \
    duckdb==1.3.0

# Set up workspace
WORKDIR /app

# Note: dbt project will be copied dynamically by the harness
# based on the dbt_project configuration in task.yaml

CMD ["bash"] 
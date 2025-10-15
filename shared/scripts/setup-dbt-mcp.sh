#!/bin/bash
# Setup dbt MCP server for installed agents
# Arguments: db_type project_type agent_name

echo "Setting up dbt MCP server..."

# Parse arguments
DB_TYPE="${1:-unknown}"
PROJECT_TYPE="${2:-unknown}"
AGENT_NAME="${3:-unknown}"

echo "Database type: $DB_TYPE"
echo "Project type: $PROJECT_TYPE"
echo "Agent: $AGENT_NAME"

# Check if project type is dbt
if [[ ! " dbt dbt-fusion " =~ " $PROJECT_TYPE " ]]; then
    echo "Skipping dbt MCP setup - '$PROJECT_TYPE' is not supported"
    exit 0
fi

# Check if database type is supported
if [[ ! " snowflake " =~ " $DB_TYPE " ]]; then
    echo "Skipping dbt MCP setup - '$DB_TYPE' is not supported"
    exit 0
fi

# Get working directory and env file location
project_dir=$(pwd)
env_file="${project_dir}/.env"

# Find dbt path
dbt_path=$(which dbt)
if [ -z "$dbt_path" ]; then
    echo "WARNING: dbt not found in PATH, skipping MCP setup"
    exit 0
fi

# Create .env file for dbt-mcp
# TODO, because this probably a janky way to do this.
cat > "$env_file" << EOF
DBT_PROJECT_DIR=$project_dir
DBT_PATH=$dbt_path
DISABLE_DBT_CLI=false
DISABLE_SEMANTIC_LAYER=true
DISABLE_DISCOVERY=true
DISABLE_ADMIN_API=true
DISABLE_SQL=true
DISABLE_DBT_CODEGEN=true
EOF

# Check if dbt-mcp is already installed (pre-installed in Docker image)
if ! command -v dbt-mcp &> /dev/null; then
    echo "dbt-mcp not found, installing..."
    uv tool install dbt-mcp --force
    echo "dbt-mcp installed"
fi

if [[ "$AGENT_NAME" == "claude" ]]; then
    echo "Registering dbt MCP server with Claude..."
    claude mcp add dbt -- uvx --env-file "$env_file" dbt-mcp
    claude mcp list

elif [[ "$AGENT_NAME" == "codex" ]]; then
    echo "Registering dbt MCP server with Codex..."
    codex mcp add dbt -- uvx --env-file "$env_file" dbt-mcp
    codex mcp list

elif [[ "$AGENT_NAME" == "gemini" ]]; then
    echo "Registering dbt MCP server with Gemini..."
    gemini mcp add dbt uvx -- --env-file "$env_file" dbt-mcp
    gemini mcp list

else
    echo "Skipping dbt MCP setup - '$AGENT_NAME' is not supported"
    exit 0
fi
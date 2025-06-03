#!/bin/bash
# Example script for running ADE-Bench

# Run with oracle agent (uses solution.sh files)
echo "Running ADE-Bench with oracle agent..."
uv run scripts_python/run_harness.py \
    --agent oracle \
    --dataset-config datasets/ade-bench-core.yaml \
    --n-concurrent-trials 2 \
    --log-level INFO

# Example with a specific task
# uv run scripts_python/run_harness.py \
#     --agent oracle \
#     --task-ids sales-aggregation-01 \
#     --log-level DEBUG

# Example with an LLM agent (when implemented)
# uv run scripts_python/run_harness.py \
#     --agent terminus \
#     --model-name anthropic/claude-3-5-sonnet \
#     --dataset-config datasets/ade-bench-core.yaml \
#     --n-concurrent-trials 1 \
#     --max-episodes 30
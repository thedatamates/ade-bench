#!/bin/bash
set -e

DATETIME=$(date +%Y%m%d_%H%M%S)

mkdir -p "profiling/summaries/${DATETIME}"

OTHER_ARGS="$@"

sudo -E env "PATH=$PATH" "HOME=$HOME" \
  py-spy record \
  -o "profiling/summaries/${DATETIME}/flamegraph.svg" \
  --subprocesses \
  -- sudo uv run scripts_python/run_harness.py \
  --with-profiling \
  --run-id "${DATETIME}" \
  ${OTHER_ARGS}

echo "${OTHER_ARGS}" >> "profiling/summaries/${DATETIME}/args"

echo "Profiling complete! results found at profiling/summaries/${DATETIME}"

#! /bin/bash
dbt deps
# remove any existing singular tests and add solution tests
rm -rf tests
mkdir tests
cp /tests/* tests

# Setup seeds and convert schema if needed
if [ -d "/seeds" ]; then
    mkdir -p seeds
    cp /seeds/* seeds/
    
    bash tests/seed-schema.sh
    
    dbt seed
fi

# run dbt data tests for evaluation
dbt test --select "test_type:singular"
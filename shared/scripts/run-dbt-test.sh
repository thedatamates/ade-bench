#! /bin/bash
# remove any existing singular tests and add solution tests
rm -rf tests
mkdir tests
cp /tests/* tests

# Run test setup script if it exists
if [ -f "tests/test_setup.sh" ]; then
    bash tests/test_setup.sh
fi

# Setup seeds and convert schema if needed
if [ -d "/seeds" ]; then
    mkdir -p seeds
    cp /seeds/* seeds/
    
    bash tests/seed-schema.sh
    
    dbt seed
fi

# run dbt data tests for evaluation
dbt test --select "test_type:singular"
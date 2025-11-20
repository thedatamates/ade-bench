#!/usr/bin/env python3

import os
import shutil
import subprocess
import argparse
import glob

parser = argparse.ArgumentParser()
parser.add_argument("--db-type", type=str, default=None)
parser.add_argument("--project-type", type=str, default=None)
parser.add_argument("--test-dir", type=str, default="/tests")  
args = parser.parse_args()

db_type = args.db_type
project_type = args.project_type
test_dir = args.test_dir

print(f"Filtering for db_type='{db_type}', project_type='{project_type}', test_dir='{test_dir}'")

if os.path.isfile("/scripts/test-setup.sh"):
    subprocess.run(["bash", "/scripts/test-setup.sh"], check=True)

if os.path.exists("tests"):
    shutil.rmtree("tests")
os.makedirs("tests", exist_ok=True)

for file_path in glob.glob(f"{test_dir}/*"):
    if not os.path.isfile(file_path):
        continue

    filename = os.path.basename(file_path)
    
    if not file_path.endswith(".sql"):
        shutil.copy(file_path, "tests/")
        continue

    include = True
    with open(file_path, "r") as f:
        content = f.read()
    
    if db_type and "-- db:" in content:
        if f"-- db:{db_type}" not in content:
            include = False
    
    if project_type and "-- project-type:" in content:
        if f"-- project-type:{project_type}" not in content:
            include = False

    if include:
        print(f"Including: {filename}")
        shutil.copy(file_path, "tests/")
    else:
        print(f"Excluding: {filename}")

if os.path.isdir("/seeds"):
    os.makedirs("seeds", exist_ok=True)
    for seed_file in glob.glob("/seeds/*"):
        if os.path.isfile(seed_file):
            shutil.copy(seed_file, "seeds/")

    if os.path.isfile("/scripts/seed-schema.sh"):
        subprocess.run(["bash", "/scripts/seed-schema.sh"], check=True)

    subprocess.run(["dbt", "seed"], check=True)

subprocess.run(["dbt", "test", "--select", "test_type:singular"], check=True)

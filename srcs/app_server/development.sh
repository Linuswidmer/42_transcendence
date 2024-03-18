#!/bin/bash

# Call the script to export environment variables
source export_env.sh

docker run -d \
    -p 127.0.0.1:5432:5432 \
    --name postgres_container \
    --env-file ../env.dev \
    -v $(pwd)/../postgres_data:/var/lib/postgresql/data \
    postgres:15

source ../../venv/bin/activate

docker run -d \
    -p 127.0.0.1:6380:6379 \
    --name redis_container \
    redis:latest

python3 manage.py runserver 127.0.0.1:8443
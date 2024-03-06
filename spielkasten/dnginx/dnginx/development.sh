#!/bin/bash

# Path to the env.dev file
env_file="../env.dev"

# Check if the file exists
if [ ! -f "$env_file" ]; then
    echo "Error: $env_file not found."
    exit 1
fi

# Read each line from the file and export variables
while IFS= read -r line; do
    # Skip empty lines or lines starting with #
    if [[ -z "$line" || "$line" == \#* ]]; then
        continue
    fi

    # Export the variable
    export "$line"

    # Echo the exported variable for confirmation
    echo "Exported: $line"
done < "$env_file"

docker stop $(docker ps -aq) && docker rm $(docker ps -aq)

docker run -d \
    -p 127.0.0.1:5432:5432 \
    --name postgres_container \
    --env-file ../env.dev \
    -v $(pwd)/../postgres_data:/var/lib/postgresql/data \
    postgres:15

source ../venv/bin/activate

python3 manage.py runserver 127.0.0.1:8443
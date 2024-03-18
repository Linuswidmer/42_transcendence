#!/bin/bash

# Path to the env.dev file
env_file="../env.dev"

# Check if the file exists
if [ ! -f "$env_file" ]; then
    echo "Error: $env_file not found."
    exit 1
fi

# Read each line from the file and export variables
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines or lines starting with #
    if [[ -z "$line" || "$line" == \#* ]]; then
        continue
    fi

    # Export the variable
    export "$line"

    # Echo the exported variable for confirmation
    echo "Exported: $line"
done < "$env_file"
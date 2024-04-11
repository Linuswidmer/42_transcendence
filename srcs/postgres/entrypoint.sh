#!/bin/bash
# Start the PostgreSQL server in the background
/usr/local/bin/docker-entrypoint.sh postgres &

# Wait for PostgreSQL to start
until psql -U pong_user -c '\l'; do
    echo "Postgres is unavailable - sleeping"
    sleep 1
done

echo "Postgres is up - executing commands"

# Run the setup script
/docker-entrypoint-initdb.d/setup_users.sh

# Bring the PostgreSQL server to the foreground
wait $!
# Use the official PostgreSQL 15 image as the base image
FROM postgres:15

# Copy the setup script to the container
COPY setup_users.sh /docker-entrypoint-initdb.d/

# Set the execute permission for the setup script
RUN chmod +x /docker-entrypoint-initdb.d/setup_users.sh

# Copy the entrypoint script to the container
COPY entrypoint.sh /

# Set the execute permission for the entrypoint script
RUN chmod +x /entrypoint.sh

# Set the entrypoint script as the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
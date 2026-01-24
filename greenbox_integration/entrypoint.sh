#!/bin/sh
set -e

# Fix permissions for the Home Assistant data directory
# This ensures ha_user can read/write options.json
if [ -d "/data" ]; then
    echo "Fixing permissions for /data..."
    chown -R ha_user:ha_user /data
fi

# Run the CMD as the non-root user
echo "Starting application as ha_user..."
exec gosu ha_user "$@"
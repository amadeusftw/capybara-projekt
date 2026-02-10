#!/bin/bash
set -e

echo "Starting application initialization..."

# Initialize database
echo "Initializing database..."
cd /code
python -c "from app.app import app, db, init_db; init_db()"

# Seed admin user if credentials are provided
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
    echo "Seeding admin user..."
    python -m flask --app app.app create-admin <<EOF
$ADMIN_USERNAME
$ADMIN_PASSWORD
$ADMIN_PASSWORD
EOF
    echo "Admin seeding complete"
else
    echo "Warning: ADMIN_USERNAME or ADMIN_PASSWORD not set. Skipping admin seeding."
fi

echo "Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app

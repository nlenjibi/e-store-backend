#!/bin/bash
set -e

echo "======================================"
echo "Starting Django E-Commerce Application"
echo "======================================"

# Get PORT from environment variable (Railway provides this)
PORT=${PORT:-8000}
echo "Port: $PORT"

# Database configuration from Railway
DB_HOST=${PGHOST:-${DB_HOST:-localhost}}
DB_PORT=${PGPORT:-${DB_PORT:-5432}}

echo "Database Host: $DB_HOST"
echo "Database Port: $DB_PORT"

# Wait for Railway PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
timeout=60
counter=0

while ! nc -z ${DB_HOST} ${DB_PORT}; do
  counter=$((counter + 1))
  if [ $counter -gt $timeout ]; then
    echo "Error: PostgreSQL connection timeout after ${timeout} seconds"
    exit 1
  fi
  echo "Waiting for PostgreSQL... ($counter/$timeout)"
  sleep 1
done

echo "✅ PostgreSQL is ready!"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput || {
  echo "❌ Migration failed!"
  exit 1
}

echo "✅ Migrations completed successfully"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || {
  echo "❌ Static files collection failed!"
  exit 1
}

echo "✅ Static files collected successfully"

# Create superuser if needed (optional - comment out if not needed)
echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Superuser created: admin / admin123')
    else:
        print('ℹ️  Superuser already exists')
except Exception as e:
    print(f'⚠️  Could not create superuser: {e}')
EOF

echo "======================================"
echo "Starting Gunicorn on 0.0.0.0:$PORT"
echo "======================================"

# Start Gunicorn
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance
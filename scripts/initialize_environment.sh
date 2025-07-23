#!/bin/env sh
set -e

APP_SERVICE="app_gl"
DB_SERVICE="db_gl"

echo "Waiting for services to be ready..."

until docker compose ps -q ${APP_SERVICE} | xargs docker inspect -f '{{.State.Running}}' | grep -q "true"; do
  echo "Waiting for ${APP_SERVICE} service to start..."
  sleep 2
done

# Get database credentials from environment variables or use defaults
DB_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-administrator}
DB_USER=${DB_USER:-gestaolegal}
DB_PASSWORD=${DB_PASSWORD:-gestaolegal}
DB_NAME=${DB_NAME:-gestaolegal}

until docker compose exec -T ${DB_SERVICE} mysqladmin ping -h localhost -u root -p${DB_ROOT_PASSWORD} --silent 2>/dev/null; do
  echo "Waiting for ${DB_SERVICE} database to be ready..."
  sleep 2
done

echo "Running initialization commands..."

ADMIN_EXISTS=$(docker compose exec -T ${DB_SERVICE} mysql -u root -p${DB_ROOT_PASSWORD} -e "SELECT COUNT(*) FROM usuarios WHERE nome='admin' LIMIT 1;" ${DB_NAME} --skip-column-names)

if [ "$ADMIN_EXISTS" -eq "0" ]; then
  echo "Admin user does not exist. Creating..."
  # Use environment variables for admin credentials or defaults
  ADMIN_EMAIL=${ADMIN_EMAIL:-admin@gl.com}
  ADMIN_PASSWORD=${ADMIN_PASSWORD:-123456}
  docker compose exec -T db_gl mysql -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} -e "CALL CreateAdmin('${ADMIN_EMAIL}', '${ADMIN_PASSWORD}');"
  echo "Admin user created successfully with email: ${ADMIN_EMAIL}"
else
  echo "Admin user already exists, skipping creation"
fi

echo "Initialization complete!"

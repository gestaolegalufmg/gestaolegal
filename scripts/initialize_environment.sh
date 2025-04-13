#!/bin/env sh
set -e

APP_CONTAINER="app_gl"
DB_CONTAINER="db_gl"

echo "Waiting for containers to be ready..."

until [ "$(docker inspect -f {{.State.Running}} ${APP_CONTAINER} 2>/dev/null)" = "true" ]; do
  echo "Waiting for ${APP_CONTAINER} container to start..."
  sleep 2
done

until docker exec ${DB_CONTAINER} mysqladmin ping -h localhost -u root -padministrator --silent 2>/dev/null; do
  echo "Waiting for ${DB_CONTAINER} database to be ready..."
  sleep 2
done

echo "Running initialization commands..."
$DC $COMPOSE_FILES exec -T ${APP_CONTAINER} bash -c "flask db upgrade"

ADMIN_EXISTS=$(docker exec ${DB_CONTAINER} mysql -u root -padministrator -e "SELECT COUNT(*) FROM usuarios WHERE nome='admin' LIMIT 1;" gestaolegal --skip-column-names)

if [ "$ADMIN_EXISTS" -eq "0" ]; then
  echo "Admin user does not exist. Creating..."
  $DC $COMPOSE_FILES exec -T ${APP_CONTAINER} bash -c "flask create-admin admin admin@gl.com 123456"
  echo "Admin user created successfully"
else
  echo "Admin user already exists, skipping creation"
fi

echo "Initialization complete!"

#!/bin/env sh
set -e

APP_SERVICE="app_gl"
DB_SERVICE="db_gl"

echo "Waiting for services to be ready..."

until docker compose ps -q ${APP_SERVICE} | xargs docker inspect -f '{{.State.Running}}' | grep -q "true"; do
  echo "Waiting for ${APP_SERVICE} service to start..."
  sleep 2
done

until docker compose exec -T ${DB_SERVICE} mysqladmin ping -h localhost -u root -padministrator --silent 2>/dev/null; do
  echo "Waiting for ${DB_SERVICE} database to be ready..."
  sleep 2
done

echo "Running initialization commands..."

ADMIN_EXISTS=$(docker compose exec -T ${DB_SERVICE} mysql -u root -padministrator -e "SELECT COUNT(*) FROM usuarios WHERE nome='admin' LIMIT 1;" gestaolegal --skip-column-names)

if [ "$ADMIN_EXISTS" -eq "0" ]; then
  echo "Admin user does not exist. Creating..."
  docker compose exec -T db_gl mysql -u gestaolegal -pgestaolegal gestaolegal -e "CALL CreateAdmin('admin@gl.com', '123456');"
  echo "Admin user created successfully"
else
  echo "Admin user already exists, skipping creation"
fi

echo "Initialization complete!"

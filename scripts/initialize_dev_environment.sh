#!/bin/env sh

set -xe

echo "Waiting for containers to be ready..."
until docker ps | grep app_gl | grep -q "Up"; do
  echo "Waiting for app_gl container to start..."
  sleep 5
done

until docker ps | grep db_gl | grep -q "Up"; do
  echo "Waiting for db_gl container to start..."
  sleep 5
done

echo "Waiting additional time for database to initialize..."
sleep 10

echo "Running initialization commands..."
docker compose --project-name development exec -T app_gl bash -c "rm -rf migrations && \
  flask db init && \
  flask db migrate && \
  flask db upgrade && \
  flask create-admin admin admin@gl.com 123456"

echo "Initialization complete!"

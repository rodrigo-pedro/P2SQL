#!/bin/bash
set -e

pg_restore -v --no-acl --no-owner  -U "$POSTGRES_USER" -d postgres /docker-entrypoint-initdb.d/sample_prompt_db

echo "Database restored successfully."

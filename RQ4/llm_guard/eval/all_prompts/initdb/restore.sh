#!/bin/bash
set -e

pg_restore -v --no-acl --no-owner  -U "$POSTGRES_USER" -d postgres /docker-entrypoint-initdb.d/llm_eval_new_examples_only_RI

echo "Database restored successfully."

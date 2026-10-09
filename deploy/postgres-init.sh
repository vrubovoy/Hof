#!/bin/bash
# Hof: PostgreSQL roles and schemas (ARCHITECTURE.md §2, §5, §5.7).
#
# The postgres image runs this once, when its data volume is empty, as the superuser over
# the local socket. Tables are not created here: each module's migrations create them under
# the module's own role.
#
# Environment, set per service in the compose file:
#   POSTGRES_DB              database the image has already created (hof)
#   HOF_DATABASES            databases to set up, space-separated: "hof" or "hof hof_test"
#   HOF_CORE_DB_PASSWORD     login password of role hof_core
#   HOF_SAECKEL_DB_PASSWORD  login password of role hof_saeckel
set -euo pipefail

: "${HOF_DATABASES:?must list the databases to set up}"
: "${HOF_CORE_DB_PASSWORD:?must be set}"
: "${HOF_SAECKEL_DB_PASSWORD:?must be set}"

run_sql() {
  psql --no-psqlrc --set ON_ERROR_STOP=1 --username "$POSTGRES_USER" --no-password "$@"
}

# Roles belong to the whole cluster, so they are created once. psql reads the passwords
# with \getenv, so they never appear in command-line arguments.
run_sql --dbname "$POSTGRES_DB" <<'SQL'
\getenv core_password HOF_CORE_DB_PASSWORD
\getenv saeckel_password HOF_SAECKEL_DB_PASSWORD
CREATE ROLE hof_core LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD :'core_password';
CREATE ROLE hof_saeckel LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD :'saeckel_password';
-- Unqualified table names in a module's SQL resolve to the module's own schema.
ALTER ROLE hof_core SET search_path = core;
ALTER ROLE hof_saeckel SET search_path = saeckel;
SQL

for db in $HOF_DATABASES; do
  if [ "$db" != "$POSTGRES_DB" ]; then
    run_sql --dbname "$POSTGRES_DB" --set db="$db" <<'SQL'
CREATE DATABASE :"db";
SQL
  fi
  # Each module role owns its schema and gets no privileges on the other one.
  # Only the superuser may create objects in public.
  run_sql --dbname "$db" <<'SQL'
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA core AUTHORIZATION hof_core;
CREATE SCHEMA saeckel AUTHORIZATION hof_saeckel;
SQL
done

// Role isolation enforced by PostgreSQL itself (ARCHITECTURE.md §2, §5; deploy/postgres-init.sh).
// Runs against hof_test in the development container from compose.dev.yaml;
// role passwords and PGPORT come from .env.

import assert from 'node:assert/strict';
import { after, before, describe, test } from 'node:test';
import { Client } from 'pg';

const DATABASE = 'hof_test';

const roles = [
  { name: 'hof_core', passwordVar: 'HOF_CORE_DB_PASSWORD', own: 'core', other: 'saeckel' },
  { name: 'hof_saeckel', passwordVar: 'HOF_SAECKEL_DB_PASSWORD', own: 'saeckel', other: 'core' },
] as const;

function passwordOf(variable: string): string {
  const password = process.env[variable];
  assert.ok(password, `${variable} is not set: create .env from .env.example`);
  return password;
}

for (const role of roles) {
  describe(`role ${role.name}`, () => {
    const client = new Client({
      database: DATABASE,
      user: role.name,
      password: passwordOf(role.passwordVar),
    });
    before(() => client.connect());
    after(() => client.end());

    test('is not a superuser and cannot create databases or roles', async () => {
      const { rows } = await client.query<{
        rolsuper: boolean;
        rolcreatedb: boolean;
        rolcreaterole: boolean;
      }>('SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname = current_user');
      assert.deepEqual(rows, [{ rolsuper: false, rolcreatedb: false, rolcreaterole: false }]);
    });

    test(`has search_path ${role.own}`, async () => {
      const { rows } = await client.query<{ search_path: string }>('SHOW search_path');
      assert.deepEqual(rows, [{ search_path: role.own }]);
    });

    test(`creates a table in ${role.own} by an unqualified name`, async () => {
      await client.query('BEGIN');
      try {
        await client.query('CREATE TABLE isolation_probe (id integer)');
        const { rows } = await client.query<{ schema: string }>(
          "SELECT relnamespace::regnamespace::text AS schema FROM pg_class WHERE relname = 'isolation_probe'",
        );
        assert.deepEqual(rows, [{ schema: role.own }]);
      } finally {
        await client.query('ROLLBACK');
      }
    });

    test(`cannot read schema ${role.other}`, async () => {
      await assert.rejects(client.query(`SELECT 1 FROM ${role.other}.isolation_probe`), {
        code: '42501',
        message: `permission denied for schema ${role.other}`,
      });
    });

    test(`cannot create a table in schema ${role.other}`, async () => {
      await assert.rejects(
        client.query(`CREATE TABLE ${role.other}.isolation_probe (id integer)`),
        {
          code: '42501',
          message: `permission denied for schema ${role.other}`,
        },
      );
    });

    test('cannot create a table in schema public', async () => {
      await assert.rejects(client.query('CREATE TABLE public.isolation_probe (id integer)'), {
        code: '42501',
        message: 'permission denied for schema public',
      });
    });

    test('cannot create a schema', async () => {
      await assert.rejects(client.query('CREATE SCHEMA isolation_probe'), {
        code: '42501',
        message: `permission denied for database ${DATABASE}`,
      });
    });
  });
}

test('a role cannot log in with the password of the other role', async () => {
  const client = new Client({
    database: DATABASE,
    user: 'hof_saeckel',
    password: passwordOf('HOF_CORE_DB_PASSWORD'),
  });
  await assert.rejects(client.connect(), { code: '28P01' });
});

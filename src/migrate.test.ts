// migrate.ts against hof_test as hof_core, with migration files from a temporary folder:
// order, a repeated run, a failed file, owner and schema of the created tables.

import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { after, afterEach, beforeEach, test } from 'node:test';
import { escapeIdentifier, Pool } from 'pg';
import { migrate } from './migrate.ts';

const password = process.env.HOF_CORE_DB_PASSWORD;
assert.ok(password, 'HOF_CORE_DB_PASSWORD is not set: create .env from .env.example');
const pool = new Pool({ database: 'hof_test', user: 'hof_core', password });

let dir = '';

beforeEach(async () => {
  const { rows } = await pool.query<{ tablename: string }>(
    "SELECT tablename FROM pg_tables WHERE schemaname = 'core'",
  );
  for (const { tablename } of rows) {
    await pool.query(`DROP TABLE ${escapeIdentifier(tablename)} CASCADE`);
  }
  dir = await mkdtemp(join(tmpdir(), 'hof-migrate-'));
});
afterEach(() => rm(dir, { recursive: true, force: true }));
after(() => pool.end());

async function writeFiles(files: Record<string, string>): Promise<void> {
  for (const [name, content] of Object.entries(files)) {
    await writeFile(join(dir, name), content);
  }
}

async function recorded(): Promise<string[]> {
  const { rows } = await pool.query<{ name: string }>(
    'SELECT name FROM schema_migrations ORDER BY name',
  );
  return rows.map((row) => row.name);
}

const CREATE_A = 'CREATE TABLE a (id integer PRIMARY KEY);';
const CREATE_B = 'CREATE TABLE b (a_id integer REFERENCES a (id));';

test('applies files in name order and records each one', async () => {
  // 002 refers to the table from 001, so it fails if the order is wrong.
  await writeFiles({ '002_b.sql': CREATE_B, '001_a.sql': CREATE_A, 'notes.txt': 'not SQL' });
  assert.deepEqual(await migrate(pool, dir), ['001_a.sql', '002_b.sql']);
  assert.deepEqual(await recorded(), ['001_a.sql', '002_b.sql']);
});

test('a repeated run applies nothing; a new file is applied alone', async () => {
  await writeFiles({ '001_a.sql': CREATE_A });
  assert.deepEqual(await migrate(pool, dir), ['001_a.sql']);
  assert.deepEqual(await migrate(pool, dir), []);
  await writeFiles({ '002_b.sql': CREATE_B });
  assert.deepEqual(await migrate(pool, dir), ['002_b.sql']);
  assert.deepEqual(await recorded(), ['001_a.sql', '002_b.sql']);
});

test('a failed migration is rolled back completely and not recorded', async () => {
  await writeFiles({
    '001_a.sql': CREATE_A,
    '002_broken.sql': 'CREATE TABLE half_done (id integer);\nSELECT 1 / 0;',
  });
  await assert.rejects(migrate(pool, dir), {
    message: 'migration 002_broken.sql failed: division by zero',
  });
  assert.deepEqual(await recorded(), ['001_a.sql']);
  const { rows } = await pool.query<{ a: string | null; half_done: string | null }>(
    "SELECT to_regclass('core.a')::text AS a, to_regclass('core.half_done')::text AS half_done",
  );
  assert.deepEqual(rows, [{ a: 'a', half_done: null }]);
});

test('tables belong to hof_core and live in schema core', async () => {
  await writeFiles({ '001_a.sql': CREATE_A });
  await migrate(pool, dir);
  const { rows } = await pool.query<{ tablename: string; schemaname: string; tableowner: string }>(
    "SELECT tablename, schemaname, tableowner FROM pg_tables WHERE tablename IN ('a', 'schema_migrations') ORDER BY tablename",
  );
  assert.deepEqual(rows, [
    { tablename: 'a', schemaname: 'core', tableowner: 'hof_core' },
    { tablename: 'schema_migrations', schemaname: 'core', tableowner: 'hof_core' },
  ]);
});

test('rejects a file name without the NNN_ prefix', async () => {
  await writeFiles({ '1_a.sql': CREATE_A });
  await assert.rejects(migrate(pool, dir), {
    message: 'migration file name must look like 001_name.sql: 1_a.sql',
  });
});

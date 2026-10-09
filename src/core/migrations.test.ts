// The Core schema created by the real migrations, against hof_test as hof_core
// (ARCHITECTURE.md §5.2–5.3). Constraints are the second line behind the application's checks.

import assert from 'node:assert/strict';
import { join } from 'node:path';
import { after, before, beforeEach, describe, test } from 'node:test';
import { escapeIdentifier, Pool } from 'pg';
import { migrate } from '../migrate.ts';

const password = process.env.HOF_CORE_DB_PASSWORD;
assert.ok(password, 'HOF_CORE_DB_PASSWORD is not set: create .env from .env.example');
const pool = new Pool({ database: 'hof_test', user: 'hof_core', password });

before(async () => {
  const { rows } = await pool.query<{ tablename: string }>(
    "SELECT tablename FROM pg_tables WHERE schemaname = 'core'",
  );
  for (const { tablename } of rows) {
    await pool.query(`DROP TABLE ${escapeIdentifier(tablename)} CASCADE`);
  }
  await migrate(pool, join(import.meta.dirname, 'migrations'));
});
beforeEach(() => pool.query('TRUNCATE sessions, users RESTART IDENTITY'));
after(() => pool.end());

async function insertUser(username: string, isAdmin = false, isDisabled = false): Promise<number> {
  const { rows } = await pool.query<{ id: number }>(
    "INSERT INTO users (username, password_hash, is_admin, is_disabled) VALUES ($1, 'hash', $2, $3) RETURNING id",
    [username, isAdmin, isDisabled],
  );
  return rows[0]!.id;
}

test('creates the columns and indexes of §5.2–5.3', async () => {
  const columns = await pool.query<Record<string, string>>(
    `SELECT table_name, column_name, data_type, is_nullable, coalesce(column_default, '') AS column_default, is_identity
       FROM information_schema.columns
      WHERE table_schema = 'core' AND table_name IN ('users', 'sessions')
      ORDER BY table_name, ordinal_position`,
  );
  assert.deepEqual(
    columns.rows.map((c) =>
      [
        c.table_name,
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        c.is_identity,
      ].join(' '),
    ),
    [
      'sessions token_hash bytea NO  NO',
      'sessions user_id integer NO  NO',
      'sessions expires_at timestamp with time zone NO  NO',
      'users id integer NO  YES',
      'users username text NO  NO',
      'users password_hash text NO  NO',
      'users is_admin boolean NO false NO',
      'users is_disabled boolean NO false NO',
    ],
  );
  const indexes = await pool.query<{ indexname: string }>(
    "SELECT indexname FROM pg_indexes WHERE schemaname = 'core' AND tablename IN ('users', 'sessions') ORDER BY indexname",
  );
  assert.deepEqual(
    indexes.rows.map((i) => i.indexname),
    ['sessions_pkey', 'sessions_user_id', 'users_one_admin', 'users_pkey', 'users_username_key'],
  );
});

describe('users', () => {
  test('accepts logins of the allowed form', async () => {
    for (const username of ['anna', '0', 'a.b_c-d', 'a'.repeat(32)]) {
      await insertUser(username);
    }
  });

  const invalid = ['Anna', '-anna', '.anna', '_anna', 'a'.repeat(33), '', 'ёлка', 'an na'];
  for (const username of invalid) {
    test(`rejects login ${JSON.stringify(username)} with 23514`, async () => {
      await assert.rejects(insertUser(username), {
        code: '23514',
        constraint: 'users_username_format',
      });
    });
  }

  test('a login is unique', async () => {
    await insertUser('anna');
    await assert.rejects(insertUser('anna'), { code: '23505', constraint: 'users_username_key' });
  });

  test('a second administrator is rejected with 23505', async () => {
    await insertUser('owner', true);
    await insertUser('anna');
    await insertUser('boris');
    await assert.rejects(insertUser('second', true), {
      code: '23505',
      constraint: 'users_one_admin',
    });
  });

  test('the administrator cannot be disabled', async () => {
    await assert.rejects(insertUser('owner', true, true), {
      code: '23514',
      constraint: 'users_admin_not_disabled',
    });
    const id = await insertUser('owner', true);
    await assert.rejects(pool.query('UPDATE users SET is_disabled = true WHERE id = $1', [id]), {
      code: '23514',
      constraint: 'users_admin_not_disabled',
    });
  });

  test('a password hash is required', async () => {
    await assert.rejects(
      pool.query("INSERT INTO users (username, password_hash) VALUES ('anna', NULL)"),
      { code: '23502' },
    );
  });
});

describe('sessions', () => {
  const token = Buffer.alloc(32, 7);

  test('a session needs an existing user', async () => {
    await assert.rejects(
      pool.query(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES ($1, 999, now() + interval '30 days')",
        [token],
      ),
      { code: '23503', constraint: 'sessions_user_id_fkey' },
    );
  });

  test('a token hash identifies one session', async () => {
    const userId = await insertUser('anna');
    const insert = () =>
      pool.query(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES ($1, $2, now() + interval '30 days')",
        [token, userId],
      );
    await insert();
    await assert.rejects(insert(), { code: '23505', constraint: 'sessions_pkey' });
  });
});

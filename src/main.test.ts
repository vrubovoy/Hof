// main.ts: common request checks — Origin (§4.6), POST body (§4.7), response headers (§4.9) —
// and the failures that stop the server before it opens the HTTP port.

import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { join } from 'node:path';
import { describe, test, type TestContext } from 'node:test';
import { createApp } from './main.ts';

const HOST = 'hof.example';
const FORM = 'application/x-www-form-urlencoded';

// Copied from ARCHITECTURE.md §4.9 on purpose: the test must not share the constant with the code.
const CSP =
  "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; media-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'";

function request(method: string, headers: Record<string, string>, body?: string) {
  return createApp().request('/anything', { method, headers, body });
}

// Silences log lines during the test and returns what was written.
function captureLog(t: TestContext): string[] {
  const lines: string[] = [];
  t.mock.method(console, 'log', (line: string) => lines.push(line));
  return lines;
}

describe('Origin', () => {
  const rejected: [string, Record<string, string>][] = [
    ['no Origin header', { host: HOST }],
    ['Origin: null', { host: HOST, origin: 'null' }],
    ['another host', { host: HOST, origin: 'https://evil.example' }],
    ['another port', { host: HOST, origin: `https://${HOST}:8443` }],
    ['http for a non-localhost host', { host: HOST, origin: `http://${HOST}` }],
    ['localhost with another port', { host: 'localhost:3000', origin: 'http://localhost:3001' }],
    ['no Host header', { origin: `https://${HOST}` }],
  ];
  for (const [name, headers] of rejected) {
    test(`rejects ${name} with 403`, async (t) => {
      const lines = captureLog(t);
      const res = await request('POST', { ...headers, 'content-type': FORM }, 'a=1');
      assert.equal(res.status, 403);
      assert.equal(lines.length, 1);
      assert.match(lines[0] ?? '', /^warn origin_rejected method=POST path=\/anything /);
    });
  }

  test('checks methods other than POST too', async (t) => {
    captureLog(t);
    assert.equal((await request('PUT', { host: HOST })).status, 403);
    assert.equal((await request('DELETE', { host: HOST })).status, 403);
  });

  const accepted: [string, Record<string, string>][] = [
    ['https://<Host>', { host: HOST, origin: `https://${HOST}` }],
    ['http://localhost:<port>', { host: 'localhost:3000', origin: 'http://localhost:3000' }],
    ['http://localhost', { host: 'localhost', origin: 'http://localhost' }],
  ];
  for (const [name, headers] of accepted) {
    test(`accepts ${name}`, async () => {
      const res = await request('POST', { ...headers, 'content-type': FORM }, 'a=1');
      assert.equal(res.status, 404);
    });
  }

  test('does not require Origin for GET and HEAD', async () => {
    assert.equal((await request('GET', { host: HOST })).status, 404);
    assert.equal((await request('HEAD', { host: HOST })).status, 404);
  });

  test('writes a hostile Origin into the log as one quoted value', async (t) => {
    const lines = captureLog(t);
    await request('POST', { host: HOST, origin: 'https://evil.example "x" y=1' });
    assert.deepEqual(lines, [
      `warn origin_rejected method=POST path=/anything origin="https://evil.example \\"x\\" y=1" host=${HOST}`,
    ]);
  });
});

describe('POST body', () => {
  const origin = { host: HOST, origin: `https://${HOST}` };

  for (const type of ['text/plain', 'multipart/form-data; boundary=x', 'application/json']) {
    test(`rejects ${type} with 415`, async () => {
      const res = await request('POST', { ...origin, 'content-type': type }, 'a=1');
      assert.equal(res.status, 415);
    });
  }

  test('rejects a POST without Content-Type with 415', async () => {
    assert.equal((await request('POST', origin)).status, 415);
  });

  test('accepts the form type with parameters and in any case', async () => {
    const type = 'Application/X-WWW-Form-Urlencoded; charset=UTF-8';
    const res = await request('POST', { ...origin, 'content-type': type }, 'a=1');
    assert.equal(res.status, 404);
  });

  const atLimit = 'a=' + 'x'.repeat(16 * 1024 - 2);
  const overLimit = atLimit + 'x';

  test('accepts exactly 16 KiB', async () => {
    const res = await request('POST', { ...origin, 'content-type': FORM }, atLimit);
    assert.equal(res.status, 404);
  });

  test('rejects 16 KiB + 1 byte with 413 by Content-Length', async () => {
    const headers = { ...origin, 'content-type': FORM, 'content-length': String(overLimit.length) };
    assert.equal((await request('POST', headers, overLimit)).status, 413);
  });

  test('rejects 16 KiB + 1 byte with 413 without Content-Length', async () => {
    const res = await request('POST', { ...origin, 'content-type': FORM }, overLimit);
    assert.equal(res.status, 413);
  });

  test('checks Origin before the body', async (t) => {
    captureLog(t);
    const res = await request('POST', { host: HOST, 'content-type': 'text/plain' }, overLimit);
    assert.equal(res.status, 403);
  });
});

describe('response headers', () => {
  test('HTML response: security headers and no-store', async () => {
    const res = await request('GET', { host: HOST });
    assert.equal(res.status, 404);
    assert.match(res.headers.get('content-type') ?? '', /^text\/html/);
    assert.equal(res.headers.get('content-security-policy'), CSP);
    assert.equal(res.headers.get('x-content-type-options'), 'nosniff');
    assert.equal(res.headers.get('referrer-policy'), 'same-origin');
    assert.equal(res.headers.get('cache-control'), 'no-store');
  });

  test('non-HTML rejection: security headers without no-store', async (t) => {
    captureLog(t);
    const res = await request('POST', { host: HOST });
    assert.equal(res.status, 403);
    assert.match(res.headers.get('content-type') ?? '', /^text\/plain/);
    assert.equal(res.headers.get('content-security-policy'), CSP);
    assert.equal(res.headers.get('x-content-type-options'), 'nosniff');
    assert.equal(res.headers.get('referrer-policy'), 'same-origin');
    assert.equal(res.headers.get('cache-control'), null);
  });
});

describe('startup', () => {
  // The server runs as a separate process with only the given environment. A listening server
  // would keep running, so exit code 1 also means the HTTP port was never opened.
  function start(env: Record<string, string>) {
    return spawnSync(process.execPath, [join(import.meta.dirname, 'main.ts')], {
      env: { PATH: process.env.PATH ?? '', ...env },
      encoding: 'utf8',
      timeout: 10_000,
    });
  }

  test('without HOF_CORE_DB_PASSWORD: exits with 1 and names the variable', () => {
    const result = start({});
    assert.equal(result.status, 1);
    assert.equal(
      result.stdout,
      'error startup_failed error="HOF_CORE_DB_PASSWORD is not set (see .env.example)"\n',
    );
  });

  test('database unavailable: exits with 1 before listening', () => {
    const result = start({ HOF_CORE_DB_PASSWORD: 'x', PGHOST: '127.0.0.1', PGPORT: '1' });
    assert.equal(result.status, 1);
    assert.equal(result.stdout, 'error startup_failed error="connect ECONNREFUSED 127.0.0.1:1"\n');
  });
});

// Hof server entry point.
// Common request checks run here, before the routes of any module (ARCHITECTURE.md §2, §4).

import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { bodyLimit } from 'hono/body-limit';
import { html } from 'hono/html';

const PORT = 3000;
const BODY_LIMIT_BYTES = 16 * 1024;

// §4.9: explicit header values, not Hono's secureHeaders preset.
const CONTENT_SECURITY_POLICY =
  "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; media-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'";

const NOT_FOUND_PAGE = html`<!doctype html>
  <html lang="ru">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Такой тропы во дворе нет</title>
    </head>
    <body>
      <h1>Такой тропы во дворе нет</h1>
    </body>
  </html>`;

type LogLevel = 'info' | 'warn' | 'error';

// §4.10: one line per event on stdout: `level event key=value ...`.
// A value with spaces, quotes or non-ASCII characters is written as a JSON string,
// so no value can break the line.
function log(level: LogLevel, event: string, fields: Record<string, string | number> = {}): void {
  const pairs = Object.entries(fields).map(([key, value]) => `${key}=${formatLogValue(value)}`);
  console.log([level, event, ...pairs].join(' '));
}

function formatLogValue(value: string | number): string {
  const text = String(value);
  return /^[!-~]+$/.test(text) && !text.includes('"') ? text : JSON.stringify(text);
}

// §4.6: Origin must be exactly https://<Host>. For localhost (development)
// http://<Host> is accepted as well. No header, `null`, another scheme, host or port — rejected.
function isAllowedOrigin(origin: string | undefined, host: string | undefined): boolean {
  if (!origin || !host) return false;
  if (origin === `https://${host}`) return true;
  return /^localhost(:\d+)?$/.test(host) && origin === `http://${host}`;
}

// §4.7: a POST body is an HTML form only; there are no file uploads.
function isFormContentType(contentType: string | undefined): boolean {
  const mediaType = contentType?.split(';', 1)[0]?.trim().toLowerCase();
  return mediaType === 'application/x-www-form-urlencoded';
}

export function createApp(): Hono {
  const app = new Hono();

  // Response headers go on every response, including the rejections below.
  app.use(async (c, next) => {
    await next();
    c.res.headers.set('Content-Security-Policy', CONTENT_SECURITY_POLICY);
    c.res.headers.set('X-Content-Type-Options', 'nosniff');
    c.res.headers.set('Referrer-Policy', 'same-origin');
    if (c.res.headers.get('Content-Type')?.startsWith('text/html')) {
      c.res.headers.set('Cache-Control', 'no-store');
    }
  });

  // CSRF: every method except GET and HEAD needs a matching Origin.
  app.use(async (c, next) => {
    if (c.req.method === 'GET' || c.req.method === 'HEAD') return next();
    const origin = c.req.header('Origin');
    const host = c.req.header('Host');
    if (!isAllowedOrigin(origin, host)) {
      log('warn', 'origin_rejected', {
        method: c.req.method,
        path: c.req.path,
        origin: origin ?? '-',
        host: host ?? '-',
      });
      return c.text('Запрос отклонён', 403);
    }
    return next();
  });

  // POST body: form type (415) and size (413).
  const limitBody = bodyLimit({
    maxSize: BODY_LIMIT_BYTES,
    onError: (c) => c.text('Слишком большой запрос', 413),
  });
  app.use(async (c, next) => {
    if (c.req.method !== 'POST') return next();
    if (!isFormContentType(c.req.header('Content-Type'))) {
      return c.text('Неподдерживаемый тип запроса', 415);
    }
    return limitBody(c, next);
  });

  // Unknown paths and methods (§4.1).
  app.notFound((c) => c.html(NOT_FOUND_PAGE, 404));

  return app;
}

if (import.meta.main) {
  serve({ fetch: createApp().fetch, port: PORT }, (info) => {
    log('info', 'start', { port: info.port });
  });
}

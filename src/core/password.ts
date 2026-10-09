// Passwords (ARCHITECTURE.md §4.3): normalisation, length rule, Argon2id hash in a PHC string,
// verification against a stored hash.
//
// Every function takes the password as typed and applies NFKC itself, so a caller cannot hash
// one form and verify another.

import { argon2, randomBytes, timingSafeEqual } from 'node:crypto';
import { promisify } from 'node:util';

export const PASSWORD_MIN_LENGTH = 15;
export const PASSWORD_MAX_LENGTH = 256;

// One profile for every installation. No tuning at startup.
const MEMORY_KIB = 19456;
const PASSES = 2;
const PARALLELISM = 1;
const SALT_BYTES = 16;
const HASH_BYTES = 32;

// Upper limits for parameters read from a stored hash. They are checked before Argon2 runs,
// so a damaged or planted string cannot make the server spend gigabytes or minutes on it.
const MAX_MEMORY_KIB = 262144;
const MAX_PASSES = 10;
const MAX_PARALLELISM = 4;

// $argon2id$v=19$m=<memory>,t=<passes>,p=<parallelism>$<salt>$<hash>
const PHC = /^\$argon2id\$v=19\$m=(\d{1,10}),t=(\d{1,10}),p=(\d{1,10})\$([^$]+)\$([^$]+)$/;

const runArgon2id = promisify(argon2);

// The same password typed on different devices may arrive in different Unicode forms:
// "й" as one code point or as "и" plus a combining mark. NFKC makes them one string.
function normalize(password: string): string {
  return password.normalize('NFKC');
}

// Length in code points, like char_length in PostgreSQL: "😀" is one character,
// although it takes two UTF-16 units in a JavaScript string.
export function passwordLength(password: string): number {
  return [...normalize(password)].length;
}

// Rule for every new password: first run, own change, initial, reset, CLI.
// Returns the error text for the form, or null if the password is acceptable.
export function newPasswordError(password: string): string | null {
  const length = passwordLength(password);
  if (length < PASSWORD_MIN_LENGTH || length > PASSWORD_MAX_LENGTH) {
    return `Пароль — от ${PASSWORD_MIN_LENGTH} до ${PASSWORD_MAX_LENGTH} символов`;
  }
  return null;
}

// PHC strings use standard base64 without "=" padding.
function encodeBase64(bytes: Buffer): string {
  return bytes.toString('base64').replace(/=+$/, '');
}

// Buffer.from(…, 'base64') silently skips characters it does not know, so the text is
// re-encoded and must come back unchanged.
function decodeBase64(text: string): Buffer | null {
  if (!/^[A-Za-z0-9+/]+$/.test(text)) return null;
  const bytes = Buffer.from(text, 'base64');
  return encodeBase64(bytes) === text ? bytes : null;
}

export async function hashPassword(password: string): Promise<string> {
  const salt = randomBytes(SALT_BYTES);
  const hash = await runArgon2id('argon2id', {
    message: Buffer.from(normalize(password)),
    nonce: salt,
    memory: MEMORY_KIB,
    passes: PASSES,
    parallelism: PARALLELISM,
    tagLength: HASH_BYTES,
  });
  return `$argon2id$v=19$m=${MEMORY_KIB},t=${PASSES},p=${PARALLELISM}$${encodeBase64(salt)}$${encodeBase64(hash)}`;
}

// valid: the password matches; wrong: it does not;
// unreadable: the stored string is not a usable Argon2id hash, so no password can match it.
export type PasswordCheck = 'valid' | 'wrong' | 'unreadable';

export async function verifyPassword(password: string, stored: string): Promise<PasswordCheck> {
  const parts = PHC.exec(stored);
  if (!parts) return 'unreadable';
  const memory = Number(parts[1]);
  const passes = Number(parts[2]);
  const parallelism = Number(parts[3]);
  const salt = decodeBase64(parts[4] ?? '');
  const expected = decodeBase64(parts[5] ?? '');
  if (memory > MAX_MEMORY_KIB || passes > MAX_PASSES || parallelism > MAX_PARALLELISM) {
    return 'unreadable';
  }
  if (!salt || !expected) return 'unreadable';

  // Parameters come from the stored string, not from the current profile: a hash made with
  // an older profile still verifies after the profile is strengthened.
  let actual: Buffer;
  try {
    actual = await runArgon2id('argon2id', {
      message: Buffer.from(normalize(password)),
      nonce: salt,
      memory,
      passes,
      parallelism,
      tagLength: expected.length,
    });
  } catch {
    // Argon2 itself refuses the parameters: salt shorter than 8 bytes, p = 0, m < 8·p and so on.
    return 'unreadable';
  }
  // timingSafeEqual throws on buffers of different length; the length check keeps that
  // out of the way even though tagLength above already makes them equal.
  return actual.length === expected.length && timingSafeEqual(actual, expected) ? 'valid' : 'wrong';
}

// Passwords (ARCHITECTURE.md §4.3). Reference hashes are built here with node:crypto directly,
// independently of hashPassword, so the PHC format itself is checked too.

import assert from 'node:assert/strict';
import { argon2Sync, randomBytes } from 'node:crypto';
import { describe, test } from 'node:test';
import { hashPassword, newPasswordError, passwordLength, verifyPassword } from './password.ts';

const PASSWORD = 'correct horse battery staple';

const b64 = (bytes: Buffer) => bytes.toString('base64').replace(/=+$/, '');

// A PHC string made without hashPassword: any parameters, salt and hash length.
function phc(
  password: string,
  { m = 19456, t = 2, p = 1, salt = randomBytes(16), hashBytes = 32 } = {},
): string {
  const hash = argon2Sync('argon2id', {
    message: Buffer.from(password.normalize('NFKC')),
    nonce: salt,
    memory: m,
    passes: t,
    parallelism: p,
    tagLength: hashBytes,
  });
  return `$argon2id$v=19$m=${m},t=${t},p=${p}$${b64(salt)}$${b64(hash)}`;
}

describe('length rule', () => {
  const cases: [string, string, boolean][] = [
    ['14 characters', 'a'.repeat(14), false],
    ['15 characters', 'a'.repeat(15), true],
    ['256 characters', 'a'.repeat(256), true],
    ['257 characters', 'a'.repeat(257), false],
    // Outside the BMP: one code point, two UTF-16 units each.
    ['14 emoji (28 UTF-16 units)', '😀'.repeat(14), false],
    ['15 emoji (30 UTF-16 units)', '😀'.repeat(15), true],
    ['256 emoji (512 UTF-16 units)', '😀'.repeat(256), true],
    ['257 emoji', '😀'.repeat(257), false],
    // Counted after NFKC: the ligature "ﬁ" becomes "fi", 14 characters become 15.
    ['13 letters + "ﬁ"', 'a'.repeat(13) + 'ﬁ', true],
  ];
  for (const [name, password, accepted] of cases) {
    test(`${name}: ${accepted ? 'accepted' : 'rejected'}`, () => {
      assert.equal(newPasswordError(password) === null, accepted);
    });
  }

  test('the error text names both limits', () => {
    assert.equal(newPasswordError('short'), 'Пароль — от 15 до 256 символов');
  });

  test('length is measured in code points after NFKC', () => {
    assert.equal(passwordLength('😀'), 1);
    assert.equal(passwordLength('ﬁ'), 2);
    assert.equal(passwordLength('й'.normalize('NFD')), 1);
  });
});

describe('hash and verify', () => {
  test('hashPassword writes the §4.3 profile as a PHC string', async () => {
    const stored = await hashPassword(PASSWORD);
    assert.match(
      stored,
      /^\$argon2id\$v=19\$m=19456,t=2,p=1\$[A-Za-z0-9+/]{22}\$[A-Za-z0-9+/]{43}$/,
    );
    // The same salt and parameters computed independently give the same hash.
    const salt = Buffer.from(stored.split('$')[4] ?? '', 'base64');
    assert.equal(stored, phc(PASSWORD, { salt }));
  });

  test('the same password gets a new salt every time', async () => {
    assert.notEqual(await hashPassword(PASSWORD), await hashPassword(PASSWORD));
  });

  test('the right password is valid, another one is wrong', async () => {
    const stored = await hashPassword(PASSWORD);
    assert.equal(await verifyPassword(PASSWORD, stored), 'valid');
    assert.equal(await verifyPassword(PASSWORD + '!', stored), 'wrong');
  });

  test('NFC and NFD forms of "й" are one password', async () => {
    const nfc = 'пароль из пятнадцати й'.normalize('NFC');
    const nfd = nfc.normalize('NFD');
    assert.notEqual(nfc, nfd);
    assert.equal(await verifyPassword(nfd, await hashPassword(nfc)), 'valid');
  });

  test('spaces are part of the password', async () => {
    const stored = await hashPassword('  spaces around it  ');
    assert.equal(await verifyPassword('spaces around it', stored), 'wrong');
  });

  test('a hash with other parameters within the limits verifies with its own parameters', async () => {
    for (const params of [
      { m: 8192, t: 3, p: 2 },
      { m: 8, t: 10, p: 1 },
      { m: 32, t: 1, p: 4 },
    ]) {
      const stored = phc(PASSWORD, params);
      assert.equal(await verifyPassword(PASSWORD, stored), 'valid', stored);
      assert.equal(await verifyPassword('another password', stored), 'wrong', stored);
    }
  });

  test('a hash of unexpected length is wrong, without an exception', async () => {
    for (const hashBytes of [31, 33, 64]) {
      const stored = phc(PASSWORD, { hashBytes });
      // Correct structure, but the hash was cut or extended by hand.
      const cut = stored.replace(/\$[^$]+$/, `$${b64(randomBytes(hashBytes))}`);
      assert.equal(await verifyPassword(PASSWORD, cut), 'wrong');
    }
  });
});

describe('unreadable hashes', () => {
  const salt = b64(randomBytes(16));
  const hash = b64(randomBytes(32));
  const cases: [string, string][] = [
    ['empty string', ''],
    ['not a PHC string', 'plain-text-password'],
    ['bcrypt', '$2b$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy'],
    ['algorithm argon2i', `$argon2i$v=19$m=19456,t=2,p=1$${salt}$${hash}`],
    ['algorithm argon2d', `$argon2d$v=19$m=19456,t=2,p=1$${salt}$${hash}`],
    ['version 16', `$argon2id$v=16$m=19456,t=2,p=1$${salt}$${hash}`],
    ['no version', `$argon2id$m=19456,t=2,p=1$${salt}$${hash}`],
    ['parameters in another order', `$argon2id$v=19$t=2,m=19456,p=1$${salt}$${hash}`],
    ['missing hash', `$argon2id$v=19$m=19456,t=2,p=1$${salt}`],
    ['m above the limit', `$argon2id$v=19$m=262145,t=2,p=1$${salt}$${hash}`],
    ['t above the limit', `$argon2id$v=19$m=19456,t=11,p=1$${salt}$${hash}`],
    ['p above the limit', `$argon2id$v=19$m=19456,t=2,p=5$${salt}$${hash}`],
    ['huge number', `$argon2id$v=19$m=99999999999,t=2,p=1$${salt}$${hash}`],
    ['base64 with a foreign character', `$argon2id$v=19$m=19456,t=2,p=1$${salt}$${hash.slice(1)}!`],
    ['base64 with padding', `$argon2id$v=19$m=19456,t=2,p=1$${salt}==$${hash}`],
    // 22 + 3 = 25 characters: no byte sequence encodes to a length of 4n + 1.
    ['base64 of impossible length', `$argon2id$v=19$m=19456,t=2,p=1$${salt}AAA$${hash}`],
    // 16 zero bytes are "A" × 22; a last "B" sets bits that do not belong to any byte.
    ['non-canonical base64', `$argon2id$v=19$m=19456,t=2,p=1$${'A'.repeat(21)}B$${hash}`],
    ['URL-safe base64', `$argon2id$v=19$m=19456,t=2,p=1$${salt}$${hash.slice(1)}_`],
    // Parameters that pass the limits but Argon2 itself refuses.
    ['salt of 4 bytes', `$argon2id$v=19$m=19456,t=2,p=1$${b64(randomBytes(4))}$${hash}`],
    ['p = 0', `$argon2id$v=19$m=19456,t=2,p=0$${salt}$${hash}`],
    ['t = 0', `$argon2id$v=19$m=19456,t=0,p=1$${salt}$${hash}`],
    ['m below 8·p', `$argon2id$v=19$m=31,t=1,p=4$${salt}$${hash}`],
    ['hash of 3 bytes', `$argon2id$v=19$m=19456,t=2,p=1$${salt}$${b64(randomBytes(3))}`],
  ];
  for (const [name, stored] of cases) {
    test(`${name} → unreadable`, async () => {
      assert.equal(await verifyPassword(PASSWORD, stored), 'unreadable');
    });
  }
});

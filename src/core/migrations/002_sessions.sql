-- Active sign-ins (ARCHITECTURE.md §4.2, §5.3). Only the SHA-256 of the cookie token is stored.
-- Revoking a session means deleting its row; expired rows are deleted on sign-in.

CREATE TABLE sessions (
  token_hash bytea PRIMARY KEY,
  user_id integer NOT NULL REFERENCES users (id),
  -- Sign-in time + 30 days, absolute.
  expires_at timestamptz NOT NULL
);

-- Ending all sessions of one user: disabling, password reset, password change.
CREATE INDEX sessions_user_id ON sessions (user_id);

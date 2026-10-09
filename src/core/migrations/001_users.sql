-- Accounts: who may sign in and who is the administrator (ARCHITECTURE.md §5.2).

CREATE TABLE users (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  -- Lower case only: the application lower-cases input, so `Anna` and `anna` are one login.
  username text NOT NULL UNIQUE
    CONSTRAINT users_username_format CHECK (username ~ '^[a-z0-9][a-z0-9._-]{0,31}$'),
  -- One PHC string: algorithm, parameters, salt and hash.
  password_hash text NOT NULL,
  is_admin boolean NOT NULL DEFAULT false,
  is_disabled boolean NOT NULL DEFAULT false,
  -- The administrator cannot be disabled.
  CONSTRAINT users_admin_not_disabled CHECK (NOT (is_admin AND is_disabled))
);

-- At most one administrator. The same index settles two simultaneous first-run submissions:
-- the second one gets a unique violation.
CREATE UNIQUE INDEX users_one_admin ON users (is_admin) WHERE is_admin;

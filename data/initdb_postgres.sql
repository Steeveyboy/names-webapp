-- Schema for PostgreSQL / Neon.
-- Compatible with the same logical structure as initdb.sql (SQLite).
-- Uses explicit types rather than SQLite-style type affinity.

DROP TABLE IF EXISTS ssa_names;

CREATE TABLE ssa_names (
    name    TEXT        NOT NULL,
    gender  CHAR(1)    NOT NULL,
    count   INTEGER    NOT NULL,
    year    INTEGER    NOT NULL
);

DROP TABLE IF EXISTS ssa_names_by_state;

CREATE TABLE ssa_names_by_state (
    state   CHAR(2)    NOT NULL,
    name    TEXT        NOT NULL,
    gender  CHAR(1)    NOT NULL,
    count   INTEGER    NOT NULL,
    year    INTEGER    NOT NULL
);

-- Performance indexes — enable index scans for name lookups
-- instead of sequential scans with LOWER().
CREATE INDEX IF NOT EXISTS idx_ssa_names_name ON ssa_names (name);
CREATE INDEX IF NOT EXISTS idx_ssa_names_year ON ssa_names (year);
CREATE INDEX IF NOT EXISTS idx_ssa_names_name_year ON ssa_names (name, year);
CREATE INDEX IF NOT EXISTS idx_ssa_names_by_state_name ON ssa_names_by_state (name);
CREATE INDEX IF NOT EXISTS idx_ssa_names_by_state_name_state ON ssa_names_by_state (name, state);

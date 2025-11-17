BEGIN TRANSACTION;

DROP TABLE IF EXISTS ssa_names;

CREATE TABLE ssa_names(
    name text,
    gender char,
    count integer,
    year integer
);

DROP TABLE IF EXISTS ssa_names_by_state;
CREATE TABLE ssa_names_by_state(
    state char(2),
    name text,
    gender char,
    count integer,
    year integer
);

COMMIT;
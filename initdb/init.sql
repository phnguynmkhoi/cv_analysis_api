CREATE TABLE person (
    id           BIGSERIAL PRIMARY KEY,
    full_name    VARCHAR(255)           NOT NULL,
    email        VARCHAR(255) UNIQUE          NOT NULL,
    phone        VARCHAR(20),
    summary      TEXT
);

CREATE TABLE education (
    id           BIGSERIAL PRIMARY KEY,
    person_id    BIGINT                  NOT NULL
                 REFERENCES person(id)   ON DELETE CASCADE,
    institution  TEXT                    NOT NULL,
    degree       VARCHAR(100),
    field        VARCHAR(255),
    start_date   VARCHAR(100),
    end_date     VARCHAR(100)
);

CREATE TABLE resume_file (
    id           BIGSERIAL PRIMARY KEY,
    person_id    BIGINT                  NOT NULL
                 REFERENCES person(id)   ON DELETE CASCADE,
    filename     TEXT,
    sha256       CHAR(64),
    storage_url  TEXT,                   
    status       VARCHAR(12)             NOT NULL
                 CHECK (status IN ('QUEUED','SUCCESS','ERROR'))
);
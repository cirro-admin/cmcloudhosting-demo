-- The whole schema.
--
-- Flyway applies this on startup and records it in a flyway_schema_history
-- table, so the same jar can be deployed against an empty database or an
-- existing one and will do the right thing either way. That is worth showing:
-- schema changes ship with the application, not as a manual step someone has
-- to remember during a release.

CREATE TABLE entries (
    id         bigserial   PRIMARY KEY,
    message    text        NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT entries_message_not_empty CHECK (length(btrim(message)) > 0),
    CONSTRAINT entries_message_length    CHECK (length(message) <= 200)
);

CREATE INDEX entries_created_at_idx ON entries (created_at DESC);

INSERT INTO entries (message) VALUES
    ('This row was created by a database migration, not by hand.'),
    ('Restart the service and this list will still be here.');

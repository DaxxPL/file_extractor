from yoyo import step


step(
    """
CREATE TABLE storage_file_metadata (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    hash TEXT NOT NULL,
    size INT NOT NULL,
    malicious BOOLEAN NOT NULL,
    sync_time TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX idx_name_hash ON storage_file_metadata (name, hash);
CREATE INDEX idx_malicious ON storage_file_metadata (malicious);
""",
    """
DROP INDEX idx_name_hash;
DROP INDEX idx_malicious;
DROP TABLE file_metadata;
""",
)

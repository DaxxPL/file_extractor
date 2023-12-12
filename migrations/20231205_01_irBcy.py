"""

"""

from yoyo import step


__depends__ = {"20230912_01_SUBzL"}

steps = [
    step(
        """
            CREATE TABLE extracted_file_metadata (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                hash TEXT NOT NULL,
                size INT NOT NULL,
                architecture TEXT,
                num_imports INT,
                num_exports INT,
                status TEXT NOT NULL,
                malicious BOOLEAN NOT NULL,
                created_at TIMESTAMP NOT NULL
            );
        CREATE UNIQUE INDEX extracted_idx_name_hash ON
        extracted_file_metadata (name, hash);
        CREATE INDEX extracted_idx_status ON
        extracted_file_metadata (status);
        CREATE INDEX extracted_idx_malicious ON
        extracted_file_metadata (malicious);

    """,
        """
DROP INDEX extracted_idx_name_hash;
DROP INDEX extracted_idx_status;
DROP INDEX extracted_idx_malicious;
DROP TABLE extracted_file_metadata;
""",
    )
]

CREATE TABLE secret_versions (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    secret_id UUID NOT NULL,

    version_number INTEGER NOT NULL,

    vault_version INTEGER NOT NULL,

    checksum VARCHAR(255),

    status VARCHAR(30) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_secret_version
        UNIQUE (secret_id, version_number),

    FOREIGN KEY (secret_id)
        REFERENCES secret_metadata(id)
        ON DELETE CASCADE

);
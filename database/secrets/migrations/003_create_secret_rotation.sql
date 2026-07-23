CREATE TABLE secret_rotation (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    secret_id UUID NOT NULL,

    rotation_frequency_days INTEGER NOT NULL,

    last_rotated_at TIMESTAMP,

    next_rotation_at TIMESTAMP NOT NULL,

    rotation_method VARCHAR(30) DEFAULT 'AUTOMATIC',

    rotation_status VARCHAR(30) DEFAULT 'SCHEDULED',

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (secret_id)
        REFERENCES secret_metadata(id)
        ON DELETE CASCADE

);
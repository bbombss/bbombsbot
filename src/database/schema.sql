CREATE TABLE IF NOT EXISTS databaseSchema
(
    schemaVersion integer NOT NULL,
    PRIMARY KEY (schemaVersion)
);  

INSERT INTO databaseSchema(schemaVersion)
SELECT 0
WHERE
NOT EXISTS (
SELECT schemaVersion FROM databaseSchema
);

CREATE TABLE IF NOT EXISTS guilds
(
    guildId bigint NOT NULL,
    PRIMARY KEY (guildId)
);

CREATE TABLE IF NOT EXISTS users
(
    userId bigint NOT NULL,
    guildId bigint NOT NULL,
    PRIMARY KEY (userId, guildId),
    FOREIGN KEY (guildId) REFERENCES guilds (guildId)
        ON DELETE CASCADE
);
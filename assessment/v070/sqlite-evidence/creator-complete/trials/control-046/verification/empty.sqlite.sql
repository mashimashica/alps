BEGIN TRANSACTION;
CREATE TABLE records (position INTEGER PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE source_state (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                snapshot_id TEXT NOT NULL, tranche INTEGER NOT NULL,
                calls_used INTEGER NOT NULL CHECK (calls_used >= 0)
            );
INSERT INTO "source_state" VALUES(1,'snap_4f53cda18c2baa0c0354bb5f',1,1);
COMMIT;

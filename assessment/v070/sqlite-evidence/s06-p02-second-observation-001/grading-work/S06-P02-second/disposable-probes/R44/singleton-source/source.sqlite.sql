BEGIN TRANSACTION;
CREATE TABLE records (position INTEGER PRIMARY KEY, payload TEXT NOT NULL);
INSERT INTO "records" VALUES(0,'{"amount_cents":407,"currency":"USD","entry_id":"ord-001","kind":"credit","posted_on":"2026-04-09","status":"settled","vendor_id":"willow"}');
CREATE TABLE source_state (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                snapshot_id TEXT NOT NULL, tranche INTEGER NOT NULL,
                calls_used INTEGER NOT NULL CHECK (calls_used >= 0)
            );
INSERT INTO "source_state" VALUES(1,'snap_84f1634697917b6d6551e89f',1,1);
COMMIT;

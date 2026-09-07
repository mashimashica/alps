BEGIN TRANSACTION;
CREATE TABLE records (position INTEGER PRIMARY KEY, payload TEXT NOT NULL);
INSERT INTO "records" VALUES(0,'{"amount_cents":407,"currency":"USD","entry_id":"ord-001","kind":"credit","posted_on":"2026-04-09","status":"settled","vendor_id":"willow"}');
INSERT INTO "records" VALUES(1,'{"amount_cents":99991,"currency":"USD","entry_id":"ord-002","kind":"charge","posted_on":"2026-04-06","status":"pending","vendor_id":"mirage"}');
INSERT INTO "records" VALUES(2,'{"amount_cents":1234,"currency":"USD","entry_id":"ord-003","kind":"charge","posted_on":"2026-04-03","status":"settled","vendor_id":"apricot"}');
INSERT INTO "records" VALUES(3,'{"amount_cents":1234,"currency":"USD","entry_id":"ord-004","kind":"credit","posted_on":"2026-04-08","status":"settled","vendor_id":"apricot"}');
INSERT INTO "records" VALUES(4,'{"amount_cents":54321,"currency":"USD","entry_id":"ord-005","kind":"charge","posted_on":"2026-04-10","status":"settled","vendor_id":"outside"}');
INSERT INTO "records" VALUES(5,'{"amount_cents":2501,"currency":"USD","entry_id":"ord-006","kind":"charge","posted_on":"2026-04-04","status":"settled","vendor_id":"juniper"}');
CREATE TABLE source_state (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                snapshot_id TEXT NOT NULL, tranche INTEGER NOT NULL,
                calls_used INTEGER NOT NULL CHECK (calls_used >= 0)
            );
INSERT INTO "source_state" VALUES(1,'snap_c22e71aa06b43ab25395e0ce',1,0);
COMMIT;

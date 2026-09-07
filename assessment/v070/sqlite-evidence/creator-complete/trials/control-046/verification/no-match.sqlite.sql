BEGIN TRANSACTION;
CREATE TABLE records (position INTEGER PRIMARY KEY, payload TEXT NOT NULL);
INSERT INTO "records" VALUES(0,'{"amount_cents":12000,"currency":"USD","entry_id":"e001","kind":"charge","posted_on":"2026-02-01","status":"settled","vendor_id":"alder"}');
INSERT INTO "records" VALUES(1,'{"amount_cents":4800,"currency":"USD","entry_id":"e002","kind":"charge","posted_on":"2026-02-02","status":"pending","vendor_id":"birch"}');
INSERT INTO "records" VALUES(2,'{"amount_cents":1500,"currency":"USD","entry_id":"e003","kind":"credit","posted_on":"2026-02-03","status":"settled","vendor_id":"alder"}');
CREATE TABLE source_state (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                snapshot_id TEXT NOT NULL, tranche INTEGER NOT NULL,
                calls_used INTEGER NOT NULL CHECK (calls_used >= 0)
            );
INSERT INTO "source_state" VALUES(1,'snap_acddd7ab4d5e89804db68ded',1,1);
COMMIT;

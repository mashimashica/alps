BEGIN TRANSACTION;
CREATE TABLE records (position INTEGER PRIMARY KEY, payload TEXT NOT NULL);
INSERT INTO "records" VALUES(0,'{"amount_cents":12000,"currency":"USD","entry_id":"e001","kind":"charge","posted_on":"2026-02-01","status":"settled","vendor_id":"alder"}');
INSERT INTO "records" VALUES(1,'{"amount_cents":4800,"currency":"USD","entry_id":"e002","kind":"charge","posted_on":"2026-02-02","status":"pending","vendor_id":"birch"}');
INSERT INTO "records" VALUES(2,'{"amount_cents":1500,"currency":"USD","entry_id":"e003","kind":"credit","posted_on":"2026-02-03","status":"settled","vendor_id":"alder"}');
INSERT INTO "records" VALUES(3,'{"amount_cents":7000,"currency":"USD","entry_id":"e004","kind":"charge","posted_on":"2026-02-04","status":"settled","vendor_id":"birch"}');
INSERT INTO "records" VALUES(4,'{"amount_cents":50000,"currency":"USD","entry_id":"e005","kind":"charge","posted_on":"2026-02-04","status":"void","vendor_id":"cedar"}');
INSERT INTO "records" VALUES(5,'{"amount_cents":9000,"currency":"USD","entry_id":"e006","kind":"charge","posted_on":"2026-01-31","status":"settled","vendor_id":"alder"}');
INSERT INTO "records" VALUES(6,'{"amount_cents":3250,"currency":"USD","entry_id":"e007","kind":"charge","posted_on":"2026-02-06","status":"settled","vendor_id":"cedar"}');
INSERT INTO "records" VALUES(7,'{"amount_cents":200,"currency":"USD","entry_id":"e008","kind":"credit","posted_on":"2026-02-06","status":"settled","vendor_id":"birch"}');
INSERT INTO "records" VALUES(8,'{"amount_cents":999,"currency":"USD","entry_id":"e009","kind":"charge","posted_on":"2026-02-08","status":"settled","vendor_id":"alder"}');
INSERT INTO "records" VALUES(9,'{"amount_cents":1200,"currency":"USD","entry_id":"e010","kind":"credit","posted_on":"2026-02-09","status":"settled","vendor_id":"dune"}');
INSERT INTO "records" VALUES(10,'{"amount_cents":8800,"currency":"USD","entry_id":"e011","kind":"charge","posted_on":"2026-02-16","status":"settled","vendor_id":"birch"}');
INSERT INTO "records" VALUES(11,'{"amount_cents":500,"currency":"USD","entry_id":"e012","kind":"charge","posted_on":"2026-02-10","status":"pending","vendor_id":"alder"}');
INSERT INTO "records" VALUES(12,'{"amount_cents":400,"currency":"USD","entry_id":"e013","kind":"charge","posted_on":"2026-02-11","status":"settled","vendor_id":"dune"}');
INSERT INTO "records" VALUES(13,'{"amount_cents":2345,"currency":"USD","entry_id":"e014","kind":"charge","posted_on":"2026-02-12","status":"settled","vendor_id":"elm"}');
INSERT INTO "records" VALUES(14,'{"amount_cents":345,"currency":"USD","entry_id":"e015","kind":"credit","posted_on":"2026-02-12","status":"void","vendor_id":"elm"}');
INSERT INTO "records" VALUES(15,'{"amount_cents":3250,"currency":"USD","entry_id":"e016","kind":"credit","posted_on":"2026-02-15","status":"settled","vendor_id":"cedar"}');
INSERT INTO "records" VALUES(16,'{"amount_cents":1001,"currency":"USD","entry_id":"e017","kind":"charge","posted_on":"2026-02-15","status":"settled","vendor_id":"alder"}');
CREATE TABLE source_state (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                snapshot_id TEXT NOT NULL, tranche INTEGER NOT NULL,
                calls_used INTEGER NOT NULL CHECK (calls_used >= 0)
            );
INSERT INTO "source_state" VALUES(1,'snap_a85a9511a684a5bb7e464198',4,1);
COMMIT;

BEGIN TRANSACTION;
CREATE TABLE records (position INTEGER PRIMARY KEY, payload TEXT NOT NULL);
INSERT INTO "records" VALUES(0,'{"amount_cents":5000,"currency":"USD","entry_id":"chg-001","kind":"charge","posted_on":"2026-06-18","status":"settled","vendor_id":"azure"}');
INSERT INTO "records" VALUES(1,'{"amount_cents":900,"currency":"USD","entry_id":"chg-002","kind":"credit","posted_on":"2026-06-10","status":"settled","vendor_id":"saffron"}');
INSERT INTO "records" VALUES(2,'{"amount_cents":123456,"currency":"USD","entry_id":"chg-003","kind":"charge","posted_on":"2026-06-13","status":"pending","vendor_id":"mirage"}');
INSERT INTO "records" VALUES(3,'{"amount_cents":700,"currency":"USD","entry_id":"chg-004","kind":"credit","posted_on":"2026-06-17","status":"settled","vendor_id":"glacier"}');
INSERT INTO "records" VALUES(4,'{"amount_cents":700,"currency":"USD","entry_id":"chg-005","kind":"charge","posted_on":"2026-06-11","status":"settled","vendor_id":"glacier"}');
INSERT INTO "records" VALUES(5,'{"amount_cents":88000,"currency":"USD","entry_id":"chg-006","kind":"charge","posted_on":"2026-06-19","status":"settled","vendor_id":"azure"}');
INSERT INTO "records" VALUES(6,'{"amount_cents":6200,"currency":"USD","entry_id":"chg-007","kind":"credit","posted_on":"2026-06-12","status":"settled","vendor_id":"azure"}');
INSERT INTO "records" VALUES(7,'{"amount_cents":900,"currency":"USD","entry_id":"chg-008","kind":"charge","posted_on":"2026-06-16","status":"settled","vendor_id":"saffron"}');
INSERT INTO "records" VALUES(8,'{"amount_cents":2222,"currency":"USD","entry_id":"chg-009","kind":"charge","posted_on":"2026-06-10","status":"settled","vendor_id":"harbor"}');
INSERT INTO "records" VALUES(9,'{"amount_cents":33333,"currency":"USD","entry_id":"chg-010","kind":"credit","posted_on":"2026-06-14","status":"void","vendor_id":"mirage"}');
INSERT INTO "records" VALUES(10,'{"amount_cents":222,"currency":"USD","entry_id":"chg-011","kind":"credit","posted_on":"2026-06-18","status":"settled","vendor_id":"harbor"}');
INSERT INTO "records" VALUES(11,'{"amount_cents":99,"currency":"USD","entry_id":"chg-012","kind":"charge","posted_on":"2026-06-09","status":"settled","vendor_id":"glacier"}');
INSERT INTO "records" VALUES(12,'{"amount_cents":0,"currency":"USD","entry_id":"chg-013","kind":"charge","posted_on":"2026-06-15","status":"settled","vendor_id":"quartz"}');
INSERT INTO "records" VALUES(13,'{"amount_cents":125,"currency":"USD","entry_id":"chg-014","kind":"charge","posted_on":"2026-06-14","status":"settled","vendor_id":"azure"}');
INSERT INTO "records" VALUES(14,'{"amount_cents":9900,"currency":"USD","entry_id":"chg-015","kind":"charge","posted_on":"2026-06-10","status":"void","vendor_id":"saffron"}');
CREATE TABLE source_state (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                snapshot_id TEXT NOT NULL, tranche INTEGER NOT NULL,
                calls_used INTEGER NOT NULL CHECK (calls_used >= 0)
            );
INSERT INTO "source_state" VALUES(1,'snap_fb322d1120ca406ad668bc26',1,0);
COMMIT;

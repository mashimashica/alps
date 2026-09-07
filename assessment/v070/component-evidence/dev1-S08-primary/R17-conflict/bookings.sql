BEGIN TRANSACTION;
CREATE TABLE operations (
                request_key TEXT PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT NOT NULL
            );
INSERT INTO "operations" VALUES('probe-conflict','{"party_id":"crew-other","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:probe-conflict","party_id":"crew-other","request_key":"probe-conflict","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
CREATE TABLE slots (
                slot_id TEXT PRIMARY KEY, starts_at TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                remaining INTEGER NOT NULL CHECK (remaining >= 0 AND remaining <= capacity)
            );
INSERT INTO "slots" VALUES('paper-lab-am','2026-10-12T09:00:00Z',6,5);
INSERT INTO "slots" VALUES('paper-lab-pm','2026-10-12T14:00:00Z',4,4);
INSERT INTO "slots" VALUES('press-demo','2026-10-13T11:00:00Z',1,1);
COMMIT;

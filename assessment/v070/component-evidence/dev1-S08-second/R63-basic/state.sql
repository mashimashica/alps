BEGIN TRANSACTION;
CREATE TABLE operations (
                request_key TEXT PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT NOT NULL
            );
INSERT INTO "operations" VALUES('normal','{"party_id":"crew-cedar","seats":2,"slot_id":"paper-lab-am"}','{"booking_id":"booking:normal","party_id":"crew-cedar","request_key":"normal","seats":2,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('unknown','{"party_id":"crew-cedar","seats":2,"slot_id":"missing-slot"}','{"party_id":"crew-cedar","reason":"unknown_slot","request_key":"unknown","seats":2,"slot_id":"missing-slot","state":"rejected"}');
INSERT INTO "operations" VALUES('too-many','{"party_id":"crew-cedar","seats":7,"slot_id":"paper-lab-am"}','{"party_id":"crew-cedar","reason":"insufficient_capacity","request_key":"too-many","seats":7,"slot_id":"paper-lab-am","state":"rejected"}');
CREATE TABLE slots (
                slot_id TEXT PRIMARY KEY, starts_at TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                remaining INTEGER NOT NULL CHECK (remaining >= 0 AND remaining <= capacity)
            );
INSERT INTO "slots" VALUES('paper-lab-am','2026-10-12T09:00:00Z',6,4);
INSERT INTO "slots" VALUES('paper-lab-pm','2026-10-12T14:00:00Z',4,4);
INSERT INTO "slots" VALUES('press-demo','2026-10-13T11:00:00Z',1,1);
COMMIT;

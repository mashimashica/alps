BEGIN TRANSACTION;
CREATE TABLE operations (
                request_key TEXT PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT NOT NULL
            );
INSERT INTO "operations" VALUES('probe-distinct-5','{"party_id":"party-5","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:probe-distinct-5","party_id":"party-5","request_key":"probe-distinct-5","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('probe-distinct-2','{"party_id":"party-2","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:probe-distinct-2","party_id":"party-2","request_key":"probe-distinct-2","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('probe-distinct-0','{"party_id":"party-0","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:probe-distinct-0","party_id":"party-0","request_key":"probe-distinct-0","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('probe-distinct-10','{"party_id":"party-10","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:probe-distinct-10","party_id":"party-10","request_key":"probe-distinct-10","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('probe-distinct-4','{"party_id":"party-4","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:probe-distinct-4","party_id":"party-4","request_key":"probe-distinct-4","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('probe-distinct-11','{"party_id":"party-11","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:probe-distinct-11","party_id":"party-11","request_key":"probe-distinct-11","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('probe-distinct-1','{"party_id":"party-1","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-1","reason":"insufficient_capacity","request_key":"probe-distinct-1","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('probe-distinct-3','{"party_id":"party-3","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-3","reason":"insufficient_capacity","request_key":"probe-distinct-3","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('probe-distinct-7','{"party_id":"party-7","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-7","reason":"insufficient_capacity","request_key":"probe-distinct-7","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('probe-distinct-8','{"party_id":"party-8","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-8","reason":"insufficient_capacity","request_key":"probe-distinct-8","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('probe-distinct-6','{"party_id":"party-6","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-6","reason":"insufficient_capacity","request_key":"probe-distinct-6","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('probe-distinct-9','{"party_id":"party-9","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-9","reason":"insufficient_capacity","request_key":"probe-distinct-9","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
CREATE TABLE slots (
                slot_id TEXT PRIMARY KEY, starts_at TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                remaining INTEGER NOT NULL CHECK (remaining >= 0 AND remaining <= capacity)
            );
INSERT INTO "slots" VALUES('paper-lab-am','2026-10-12T09:00:00Z',6,0);
INSERT INTO "slots" VALUES('paper-lab-pm','2026-10-12T14:00:00Z',4,4);
INSERT INTO "slots" VALUES('press-demo','2026-10-13T11:00:00Z',1,1);
COMMIT;

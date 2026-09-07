BEGIN TRANSACTION;
CREATE TABLE operations (
                request_key TEXT PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT NOT NULL
            );
INSERT INTO "operations" VALUES('shared-0','{"party_id":"party-0","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:shared-0","party_id":"party-0","request_key":"shared-0","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('shared-9','{"party_id":"party-9","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:shared-9","party_id":"party-9","request_key":"shared-9","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('shared-3','{"party_id":"party-3","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:shared-3","party_id":"party-3","request_key":"shared-3","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('shared-4','{"party_id":"party-4","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:shared-4","party_id":"party-4","request_key":"shared-4","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('shared-8','{"party_id":"party-8","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:shared-8","party_id":"party-8","request_key":"shared-8","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('shared-7','{"party_id":"party-7","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:shared-7","party_id":"party-7","request_key":"shared-7","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('shared-2','{"party_id":"party-2","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-2","reason":"insufficient_capacity","request_key":"shared-2","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('shared-11','{"party_id":"party-11","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-11","reason":"insufficient_capacity","request_key":"shared-11","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('shared-6','{"party_id":"party-6","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-6","reason":"insufficient_capacity","request_key":"shared-6","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('shared-1','{"party_id":"party-1","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-1","reason":"insufficient_capacity","request_key":"shared-1","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('shared-5','{"party_id":"party-5","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-5","reason":"insufficient_capacity","request_key":"shared-5","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('shared-10','{"party_id":"party-10","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-10","reason":"insufficient_capacity","request_key":"shared-10","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
CREATE TABLE slots (
                slot_id TEXT PRIMARY KEY, starts_at TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                remaining INTEGER NOT NULL CHECK (remaining >= 0 AND remaining <= capacity)
            );
INSERT INTO "slots" VALUES('paper-lab-am','2026-10-12T09:00:00Z',6,0);
INSERT INTO "slots" VALUES('paper-lab-pm','2026-10-12T14:00:00Z',4,4);
INSERT INTO "slots" VALUES('press-demo','2026-10-13T11:00:00Z',1,1);
COMMIT;

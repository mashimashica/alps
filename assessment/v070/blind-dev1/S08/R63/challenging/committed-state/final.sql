BEGIN TRANSACTION;
CREATE TABLE operations (
                request_key TEXT PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT NOT NULL
            );
INSERT INTO "operations" VALUES('cobalt-linocut-20261122-01','{"party_id":"team-cobalt","seats":4,"slot_id":"linocut-sun-am"}','{"booking_id":"booking:cobalt-linocut-20261122-01","party_id":"team-cobalt","request_key":"cobalt-linocut-20261122-01","seats":4,"slot_id":"linocut-sun-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('orchid-linocut-20261122-01','{"party_id":"crew-orchid","seats":3,"slot_id":"linocut-sun-am"}','{"party_id":"crew-orchid","reason":"insufficient_capacity","request_key":"orchid-linocut-20261122-01","seats":3,"slot_id":"linocut-sun-am","state":"rejected"}');
CREATE TABLE slots (
                slot_id TEXT PRIMARY KEY, starts_at TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                remaining INTEGER NOT NULL CHECK (remaining >= 0 AND remaining <= capacity)
            );
INSERT INTO "slots" VALUES('linocut-sun-am','2026-11-22T09:00:00Z',5,1);
INSERT INTO "slots" VALUES('linocut-sun-pm','2026-11-22T14:00:00Z',6,6);
INSERT INTO "slots" VALUES('stencil-demo-mon','2026-11-23T10:30:00Z',2,2);
COMMIT;

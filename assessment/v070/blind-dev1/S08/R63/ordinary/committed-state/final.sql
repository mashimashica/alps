BEGIN TRANSACTION;
CREATE TABLE operations (
                request_key TEXT PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT NOT NULL
            );
INSERT INTO "operations" VALUES('riso-moss-20261116-01','{"party_id":"moss-bookclub","seats":2,"slot_id":"risograph-mon-pm"}','{"booking_id":"booking:riso-moss-20261116-01","party_id":"moss-bookclub","request_key":"riso-moss-20261116-01","seats":2,"slot_id":"risograph-mon-pm","state":"confirmed"}');
INSERT INTO "operations" VALUES('iris-screenprint-20261116-01','{"party_id":"team-iris","seats":3,"slot_id":"screenprint-mon-am"}','{"booking_id":"booking:iris-screenprint-20261116-01","party_id":"team-iris","request_key":"iris-screenprint-20261116-01","seats":3,"slot_id":"screenprint-mon-am","state":"confirmed"}');
CREATE TABLE slots (
                slot_id TEXT PRIMARY KEY, starts_at TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                remaining INTEGER NOT NULL CHECK (remaining >= 0 AND remaining <= capacity)
            );
INSERT INTO "slots" VALUES('screenprint-mon-am','2026-11-16T09:30:00Z',8,5);
INSERT INTO "slots" VALUES('risograph-mon-pm','2026-11-16T14:00:00Z',6,4);
INSERT INTO "slots" VALUES('paper-marbling-tue','2026-11-17T10:00:00Z',3,3);
COMMIT;

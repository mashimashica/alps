BEGIN TRANSACTION;
CREATE TABLE operations (
                request_key TEXT PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT NOT NULL
            );
INSERT INTO "operations" VALUES('req-639e584d6c9743a8b40afeb23ce3d608','{"party_id":"party-1","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:req-639e584d6c9743a8b40afeb23ce3d608","party_id":"party-1","request_key":"req-639e584d6c9743a8b40afeb23ce3d608","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('req-82e44764c5db42faacf242ccfbf1b908','{"party_id":"party-6","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:req-82e44764c5db42faacf242ccfbf1b908","party_id":"party-6","request_key":"req-82e44764c5db42faacf242ccfbf1b908","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('req-e8f534fae37c467eb11a21b6b00cbee7','{"party_id":"party-5","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:req-e8f534fae37c467eb11a21b6b00cbee7","party_id":"party-5","request_key":"req-e8f534fae37c467eb11a21b6b00cbee7","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('req-a7ec0e029f2c42eebac9c03a9a2f4293','{"party_id":"party-8","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:req-a7ec0e029f2c42eebac9c03a9a2f4293","party_id":"party-8","request_key":"req-a7ec0e029f2c42eebac9c03a9a2f4293","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('req-9a6d112496dc452586379436eaffa4d5','{"party_id":"party-7","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:req-9a6d112496dc452586379436eaffa4d5","party_id":"party-7","request_key":"req-9a6d112496dc452586379436eaffa4d5","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('req-2628e9eafc8c46ee9f970b092ef1d213','{"party_id":"party-3","seats":1,"slot_id":"paper-lab-am"}','{"booking_id":"booking:req-2628e9eafc8c46ee9f970b092ef1d213","party_id":"party-3","request_key":"req-2628e9eafc8c46ee9f970b092ef1d213","seats":1,"slot_id":"paper-lab-am","state":"confirmed"}');
INSERT INTO "operations" VALUES('req-c0eb4ac8fece41aaa2ead46544b80183','{"party_id":"party-4","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-4","reason":"insufficient_capacity","request_key":"req-c0eb4ac8fece41aaa2ead46544b80183","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('req-cd0c2d7fc6874c3fbbbed9ce1418b860','{"party_id":"party-0","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-0","reason":"insufficient_capacity","request_key":"req-cd0c2d7fc6874c3fbbbed9ce1418b860","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('req-88e8d5508a2b4e9aae7f106cb9c09020','{"party_id":"party-10","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-10","reason":"insufficient_capacity","request_key":"req-88e8d5508a2b4e9aae7f106cb9c09020","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('req-2738d88162344b81b01e208d77b8634b','{"party_id":"party-2","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-2","reason":"insufficient_capacity","request_key":"req-2738d88162344b81b01e208d77b8634b","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('req-c07201fe7cf44d4890d318f94ec158bb','{"party_id":"party-11","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-11","reason":"insufficient_capacity","request_key":"req-c07201fe7cf44d4890d318f94ec158bb","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
INSERT INTO "operations" VALUES('req-9622568965c34b63b713c1a86d204749','{"party_id":"party-9","seats":1,"slot_id":"paper-lab-am"}','{"party_id":"party-9","reason":"insufficient_capacity","request_key":"req-9622568965c34b63b713c1a86d204749","seats":1,"slot_id":"paper-lab-am","state":"rejected"}');
CREATE TABLE slots (
                slot_id TEXT PRIMARY KEY, starts_at TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                remaining INTEGER NOT NULL CHECK (remaining >= 0 AND remaining <= capacity)
            );
INSERT INTO "slots" VALUES('paper-lab-am','2026-10-12T09:00:00Z',6,0);
INSERT INTO "slots" VALUES('paper-lab-pm','2026-10-12T14:00:00Z',4,4);
INSERT INTO "slots" VALUES('press-demo','2026-10-13T11:00:00Z',1,1);
COMMIT;

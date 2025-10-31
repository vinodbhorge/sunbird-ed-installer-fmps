-- Create keyspace
CREATE KEYSPACE IF NOT EXISTS sb_collection_tracking
WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};


CREATE TABLE IF NOT EXISTS sb_collection_tracking.batches (
    activityid text,
    activitytype text,
    batchid text,
    cert_templates map<text, frozen<map<text, text>>>,
    created_date timestamp,
    createdby text,
    createdfor list<text>,
    description text,
    end_date timestamp,
    enrollment_enddate timestamp,
    enrollmenttype text,
    name text,
    start_date timestamp,
    status int,
    updated_date timestamp,
    PRIMARY KEY (activityid, batchid)
) WITH CLUSTERING ORDER BY (batchid ASC);

DROP MATERIALIZED VIEW IF EXISTS sb_collection_tracking.batches_by_id;
CREATE MATERIALIZED VIEW sb_collection_tracking.batches_by_id AS
    SELECT batchid, activityid, activitytype
    FROM sb_collection_tracking.batches
    WHERE batchid IS NOT NULL AND activityid IS NOT NULL
    PRIMARY KEY (batchid, activityid)
    WITH CLUSTERING ORDER BY (activityid ASC)
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = 'MV: read by batchid (only immutable columns)'
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'chunk_length_in_kb': '64', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND dclocal_read_repair_chance = 0.1
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair_chance = 0.0
    AND speculative_retry = '99PERCENTILE';

-- User enrolments table
CREATE TABLE IF NOT EXISTS sb_collection_tracking.user_enrolments (
    userid text,
    activityid text,
    activitytype text,
    batchid text,
    active boolean,
    addedby text,
    completedon timestamp,
    datetime timestamp,
    enrolled_date timestamp,
    issued_certificates list<frozen<map<text, text>>>,
    optional_batches list<text>,
    progress int,
    status int,
    statusmap map<text, int>,
    PRIMARY KEY (userid, activityid, activitytype, batchid)
) WITH CLUSTERING ORDER BY (activityid ASC, activitytype ASC, batchid ASC);

-- User enrolments table view
DROP MATERIALIZED VIEW IF EXISTS sb_collection_tracking.enrollments_by_batch;
CREATE MATERIALIZED VIEW sb_collection_tracking.enrollments_by_batch AS
    SELECT activityid, activitytype, batchid, userid, active, addedby, completedon, datetime, enrolled_date, issued_certificates, optional_batches, progress, status, statusmap
    FROM sb_collection_tracking.user_enrolments
    WHERE activityid IS NOT NULL AND activitytype IS NOT NULL AND batchid IS NOT NULL AND userid IS NOT NULL
    PRIMARY KEY ((activityid, activitytype, batchid), userid)
    WITH CLUSTERING ORDER BY (userid ASC);

-- Insert values into role and role group.

INSERT INTO sunbird.role_group (id, name) VALUES ('SKILLDOMAIN_CREATOR', 'SkillDomain Creator');
INSERT INTO sunbird.role_group (id, name) VALUES ('SKILLDOMAIN_REVIEWER', 'SkillDomain Reviewer');
INSERT INTO sunbird.role (id, name, rolegroupid, status) VALUES ('SKILLDOMAIN_REVIEWER', 'SkillDomain Reviewer', ['SKILLDOMAIN_REVIEWER'],1);
INSERT INTO sunbird.role (id, name, rolegroupid, status) VALUES ('SKILLDOMAIN_CREATOR', 'SkillDomain Creator', ['SKILLDOMAIN_CREATOR'],1);
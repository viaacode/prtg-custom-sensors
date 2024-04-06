-- Summary of database status
-- - replication delay (is always 0 on primary database as pg_last_xact_replay_timestamp() returns NULL)
-- - database size estimated using size of default tablespace
-- - number of client session

select
  coalesce(EXTRACT(EPOCH FROM now() - pg_last_xact_replay_timestamp()),0) as replication_delay,
  pg_tablespace_size('pg_default') as size,
  count(datid) as sessions from pg_stat_activity
;

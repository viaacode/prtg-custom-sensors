-- the database is a hot standby
-- calculates the time elapsed since the most recent replayed transaction in hours
select EXTRACT(EPOCH FROM now() - pg_last_xact_replay_timestamp())/3600;

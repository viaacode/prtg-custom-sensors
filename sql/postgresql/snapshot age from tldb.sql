-- Database snapshots of databases are restored in docker containres for ETL
-- purposes. The timesatmp of these snapshots are stored in the syncs table
-- when the container is created.
-- syncstatus=# select * from syncs
--     service     |             time
--    -----------------+-------------------------------
--     mediahaven-reco | 2020-08-26 10:03:53.175629+00
--     sb-testbeeldond | 2020-07-02 20:07:00+00
--     mediamosa       | 2020-07-01 21:04:00+00
--     mediahaven      | 2020-08-25 23:04:41.194525+00
--     ams             | 2020-08-25 19:00:01+00
--     teamleader      | 2020-06-17 15:02:42.778838+00

select EXTRACT(EPOCH FROM now() - time)/3600 from syncs where service = @prtg;

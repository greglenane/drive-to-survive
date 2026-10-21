-- Empty picks sheets can produce unnamed rows for upcoming rounds.
-- Exclude them before dashboard queries choose the latest round.
SELECT * FROM read_parquet('s3://greglenane-drive-to-survive/scored_aggregate.parquet')
WHERE Name IS NOT NULL AND trim(Name) <> '';

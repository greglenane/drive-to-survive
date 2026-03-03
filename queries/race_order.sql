select distinct Race, Round,
concat(Round::INT, ' - ', Race) as round_race
from s3_data.scored_aggregate
order by Round desc
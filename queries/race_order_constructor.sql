select distinct raceName AS Race
from s3_data.results_scored
order by round::INT
select 
    *,
    concat(Driver_givenName, Driver_familyName) AS Driver,
    raceName AS Race
from s3_data.results_scored 
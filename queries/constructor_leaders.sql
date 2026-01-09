select
    Constructor_name AS Constructor,
    round AS Round,
    Race,
    sum(total) As Total
from (select 
        *,
        concat(Driver_givenName, Driver_familyName) AS Driver,
        raceName AS Race
    from s3_data.results_scored)
group by Constructor, Round, Race
order by Round, Total desc
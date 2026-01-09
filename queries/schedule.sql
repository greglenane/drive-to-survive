select
    s.round AS Round,
    s.racename AS Race,
    s.racedate_est AS "Race Date",
    s.racetime_est AS "Race Time",
    s.qualifyingdate_est as "Qualifying Date",
    s.qualifyingtime_est AS "Qualifying Time",
    CASE 
        WHEN s.sprintdate_est < '1971-01-01' OR s.sprintdate_est IS NULL THEN '-'
        ELSE strftime(s.sprintdate_est, '%Y-%m-%d')
    END AS "Sprint Date",
    s.sprinttime_est AS "Sprint Time"
from s3_data.schedule s
order by s.round::INT asc
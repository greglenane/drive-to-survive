
select
    Name,
    cumulative_var AS "Cumulative Variance"
from s3_data.scored_aggregate
where Round = (select max(Round) from s3_data.scored_aggregate)
order by cumulative_var desc
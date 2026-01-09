
select
    Name,
    cumulative_var
from s3_data.scored_aggregate
where Round = (select max(Round) from s3_data.scored_aggregate)
order by cumulative_var desc
select
    Name,
    count(*) as "Most 10s"
from s3_data.scored_aggregate
where total = 10
group by Name
order by "Most 10s" desc;
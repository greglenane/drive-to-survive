select
    Name,
    count(*) as "Goose Eggs"
from s3_data.scored_aggregate
where total = 0
group by Name
order by "Goose Eggs" desc;
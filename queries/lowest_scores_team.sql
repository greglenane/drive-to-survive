select team_name, 
       sum(gp) as total_low
from s3_data.scored_aggregate
where gp < 0
group by 1
order by total_low 
limit 1
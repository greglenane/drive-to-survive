with recent_races as (
  select 
  s.Round,
  s.Name,
  s.Driver,
  s.Race,
  s.gp,
  s.fastest_lap,
  s.sprint,
  s.total,
  s.cumulative_total
from s3_data.scored_aggregate s
where Round = (select max(Round) from s3_data.scored_aggregate)
order by s.total desc
)
select 
  distinct rr.Name
from recent_races rr
order by rr.cumulative_total desc
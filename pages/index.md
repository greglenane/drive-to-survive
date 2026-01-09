---
title: Drive To Survive
---

```sql scored_aggregate
  select
      *
  from s3_data.scored_aggregate
  order by Round, total desc
```
```sql race_list
  select distinct Race, Round
  from s3_data.scored_aggregate
  order by Round asc
```
```sql year
select 
  max(season) as season
from s3_data.schedule
```
```sql winning
  select 
    distinct rr.Name
  from ${recent_races} rr
  order by rr.cumulative_total desc
```

<div style="text-align: center; font-size: 2rem;">
    <Value data={year} column="season" /> Standings
</div>

<BarChart
    data={scored_aggregate}
    x=Name
    y=total
    series=Race
    swapXY=true
    labels=true
    stackTotalLabel=true
    labelPosition=outside
    labelColor=transparent
    stackTotalLabelColor=white
    seriesOrder={race_list.map(x => x.Race)}
    chartAreaHeight=300
/>

<LineChart
    data={scored_aggregate}
    x=Round
    y=cumulative_total
    series=Name
    seriesOrder={winning.map(x => x.Name)}
    step=true
    lineWidth=3
    chartAreaHeight=500
/>


```sql recent_races
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
```

<div style="text-align: center; font-size: 1.5rem;">
    Round <Value data={recent_races} column="Round" row=1 /> <Value data={recent_races} column=Race row=1/> Results
</div>
<DataTable 
  data={recent_races}
  rows=all>
  <Column id=Name />
  <Column id=Driver />
  <Column id=Race/>
  <Column id=gp title="GP Points" />
  <Column id=fastest_lap title="Fastest Lap"/>
  <Column id=sprint title="Sprint Points" />
  <Column id=total title="Total Points" contentType=bar barColor="#CCFF00" />
</DataTable>
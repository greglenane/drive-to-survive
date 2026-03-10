---
title: Drive To Survive
full_width: true
queries:
    - scored_aggregate.sql
    - year.sql
    - win_probability.sql
    - race_order.sql
    - winning.sql
    - team_scoring.sql
    - lowest_scores.sql
    - lowest_scores_team.sql
---

<div style="text-align: center; font-size: 2rem;">
    <Value data={year} column="season" /> Player Standings
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
    seriesOrder={race_order.map(x => x.Race)}
    rightPadding=90
    chartAreaHeight=250
    yMin={lowest_scores[0].total_low}
    echartsOptions={{
        xAxis: {
            position: 'bottom'
        }
    }}
/>

<div style="text-align: center; font-size: 2rem;">
    <Value data={year} column="season" /> Team Standings
</div>
<BarChart
    data={team_scoring}
    x=team_name
    y=team_total
    series=Race
    swapXY=true
    labels=true
    stackTotalLabel=true
    labelPosition=outside
    labelColor=transparent
    stackTotalLabelColor=white
    seriesOrder={race_order.map(x => x.Race)}
    rightPadding=90
    chartAreaHeight=250
    yMin={lowest_scores_team[0].total_low}
    echartsOptions={{
        xAxis: {
            position: 'bottom'
        }
    }}
/>

<Dropdown
    data={race_order} 
    name=Race
    value=Round
    label=round_race 
    title="Round:"
    defaultValue={race_order[0].Round}
    order=Round
/>

```sql race_table
select 
  s.Round,
  s.Name,
  s.Team_Name,
  s.Driver,
  s.Race,
  s.gp,
  s.fastest_lap,
  s.sprint,
  s.total,
  s.cumulative_total
from s3_data.scored_aggregate s
where s.Round = ${inputs.Race.value}
order by s.total desc
```

<div style="text-align: center; font-size: 1.5rem;">
    Round <Value data={race_table} column="Round" row=0 /> <Value data={race_table} column=Race row=0/> Results
</div>
<DataTable 
  data={race_table}
  rows=all
  rowShading=true>
  <Column id=Name align=left/>
  <Column id=team_name align=left/>
  <Column id=Driver align=left/>
  <Column id=Round align=left/>
  <Column id=Race align=left/>
  <Column id=gp title="GP Points" align=left/>
  <Column id=fastest_lap title="Fastest Lap" align=left/>
  <Column id=sprint title="Sprint Points" align=left/>
  <Column id=total title="Total Points" contentType=bar barColor="#00ff26"/>
</DataTable>

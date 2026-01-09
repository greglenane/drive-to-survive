---
title: Drive To Survive
full_width: true
queries:
    - scored_aggregate.sql
    - year.sql
    - race_order.sql
    - winning.sql
    - recent_race.sql
---

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
    seriesOrder={race_order.map(x => x.Race)}
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

<div style="text-align: center; font-size: 1.5rem;">
    Round <Value data={recent_race} column="Round" row=1 /> <Value data={recent_race} column=Race row=1/> Results
</div>
<DataTable 
  data={recent_race}
  rows=all
  rowShading=true>
  <Column id=Name />
  <Column id=Driver />
  <Column id=Race/>
  <Column id=gp title="GP Points" />
  <Column id=fastest_lap title="Fastest Lap"/>
  <Column id=sprint title="Sprint Points" />
  <Column id=total title="Total Points" contentType=bar barColor="#CCFF00" />
</DataTable>
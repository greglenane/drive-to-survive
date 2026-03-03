---
title: Drive To Survive
full_width: true
queries:
    - scored_aggregate.sql
    - year.sql
    - win_probability.sql
    - race_order.sql
    - winning.sql
    - recent_race.sql
    - team_scoring.sql
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
    chartAreaHeight=300
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
    chartAreaHeight=300
/>

<div style="text-align: center; font-size: 1.5rem;">
    Round <Value data={recent_race} column="Round" row=1 /> <Value data={recent_race} column=Race row=1/> Results
</div>
<DataTable 
  data={recent_race}
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
  <Column id=total title="Total Points" contentType=bar barColor="#CCFF00"/>
</DataTable>

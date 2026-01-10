---
title: League Stats
sidebar_position: 3
full_width: true
queries:
    - yea.sqlr.sql
    - scored_aggregate.sql
    - winning.sql
    - player_var.sql
    - goose_eggs.sql
---

<div style="text-align: center; font-size: 2rem;">
    <Value data={year} column="season" /> Standings
</div>
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

<div style="text-align: center; font-size: 2rem;">
    Variance From Expected Points
</div>
<BarChart
    subtitle="Variance uses expected points of grid position in GP and Sprint and compares with actual results. Positive #'s are 'lucky'"
    data={player_var}
    x=Name
    y="Cumulative Variance"
    series=Name
    labels=true
    labelPosition=outside
    chartAreaHeight=500
/>

<div style="text-align: center; font-size: 2rem;">
    Most Goose Eggs
</div>
<BarChart
    data={goose_eggs}
    x=Name
    y="Goose Eggs"
    series=Name
    labels=true
    labelPosition=outside
    chartAreaHeight=500
/>
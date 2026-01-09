---
title: League Stats
sidebar_position: 3
full_width: true
queries:
    - player_var.sql
---

<div style="text-align: center; font-size: 2rem;">
    Variance From Expected Points
</div>
<BarChart
    subtitle="Variance uses expected points of grid position in GP and Sprint and compares with actual results. Positive #'s are 'lucky'"
    data={player_var}
    x=Name
    y=cumulative_var
    labels=true
    labelPosition=outside
    chartAreaHeight=300
/>
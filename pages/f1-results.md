---
title: F1 Leaders
sidebar_position: 2
full_width: true
queries:
    - all_drivers.sql
    - race_order_constructor.sql
    - constructor_leaders.sql
---

<div style="text-align: center; font-size: 2rem;">
    F1 Leaders
</div>
<BarChart
    data={all_drivers}
    x=Driver
    y=total
    series=Race
    swapXY=true
    labels=true
    stackTotalLabel=true
    labelPosition=outside
    labelColor=transparent
    stackTotalLabelColor=white
    seriesOrder={race_order_constructor.map(x => x.Race)}
    chartAreaHeight=300
/>

<div style="text-align: center; font-size: 2rem;">
    Constructor Leaders
</div>
<BarChart
    data={constructor_leaders}
    x=Constructor
    y=Total
    series=Race
    swapXY=true
    labels=true
    stackTotalLabel=true
    labelPosition=outside
    labelColor=transparent
    stackTotalLabelColor=white
    seriesOrder={race_order_constructor.map(x => x.Race)}
    chartAreaHeight=300
/>
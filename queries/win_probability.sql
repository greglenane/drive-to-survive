with base as (
    select
        Name,
        round,
        cumulative_total as current_points
    from s3_data.scored_aggregate
),

calc as (
    select
        Name,
        round,
        current_points,
        (24 - round) * 15 as max_remaining_points,
        current_points + (24 - round) * 15 as championship_potential
    from base
),

leaders as (
    select
        round,
        max(current_points) as max_current_points
    from calc
    group by round
),

eligible as (
    select
        c.*,
        l.max_current_points,
        case
            when c.championship_potential >= l.max_current_points then 1
            else 0
        end as can_win
    from calc c
    join leaders l on c.round = l.round
),

softmax as (
    select
        *,
        case
            when can_win = 1 then exp(championship_potential / 12.0)  -- temperature
            else 0
        end as exp_pot
    from eligible
),

final as (
    select
        Name,
        round,
        case
            when can_win = 1 then exp_pot / sum(exp_pot) over (partition by round)
            else 0
        end as win_probability
    from softmax
)

select *
from final
order by round desc, win_probability desc;
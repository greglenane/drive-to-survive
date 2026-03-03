WITH team_round_totals AS (
    -- First, we aggregate the two individuals into a single team row per round
    SELECT
        team,
        team_name,
        round,
        race,
        sum(total) as team_total,
        sum(total_expected) as team_total_expected,
        sum(total_var) as team_total_var,
        -- Including your other metrics
        sum(gp_expected) as team_gp_expected,
        sum(gp) as team_gp,
        sum(gp_var) as team_gp_var,
        sum(fastest_lap) as team_fastest_lap,
        sum(sprint_expected) as team_sprint_expected,
        sum(sprint) as team_sprint,
        sum(sprint_var) as team_sprint_var
    FROM s3_data.scored_aggregate
    GROUP BY team, team_name, round, race
)
SELECT 
    *,
    SUM(team_total) OVER (
        PARTITION BY team_name 
        ORDER BY round 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_team_total,
    
    SUM(team_total_expected) OVER (
        PARTITION BY team_name 
        ORDER BY round 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_team_expected,
    
    SUM(team_total_var) OVER (
        PARTITION BY team_name 
        ORDER BY round 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_team_var
FROM team_round_totals
ORDER BY round ASC, cumulative_team_total DESC;
# Drive to Survive: F1 Fantasy Scoreboard

[![F1 ETL and Dashboard Deploy](https://github.com/greglenane/drive-to-survive/actions/workflows/deploy.yml/badge.svg)](https://github.com/greglenane/drive-to-survive/actions/workflows/deploy.yml)

An automated fantasy league engine and analytics dashboard for Formula 1. This project handles the end-to-end lifecycle of a fantasy season: from extracting live race results to calculating league standings and visualizing performance trends.

## Live Scoreboard
**View the standings here:** [https://greglenane.github.io/drive-to-survive/](https://greglenane.github.io/drive-to-survive/)

---

## League Mechanics & Scoring

The **premise** of this league is to select an F1 driver for each GP weekend who places as close to 10th place as possible. Since the top ~5 drivers are fairly consistent, there is not much excitement in selecting the winner. This league aims to select the most "average" driver. GP and Sprint points awarded are determined by finishing position in the respective race event, whereas Fastest Lap points are awarded based on rank within the **field** (the driver with the 10th fastest lap receives 1 bonus point).

### Scoring Ruleset
Points are calculated automatically by the ETL pipeline:

| Position | GP Points | Sprint Points | Fastest Lap |
| :--- | :--- | :--- | :--- |
| 1 | -3 | 0 | 0 |
| 2 | -2 | 0 | 0 |
| 3 | -1 | 0 | 0 |
| 4 | 0 | 0 | 0 |
| 5 | 1 | 0 | 0 |
| 6 | 2 | 0 | 0 |
| 7 | 4 | 1 | 0 |
| 8 | 6 | 2 | 0 |
| 9 | 8 | 3 | 0 |
| **10** | **10** | **4** | **1** |
| 11 | 8 | 3 | 0 |
| 12 | 6 | 2 | 0 |
| 13 | 4 | 1 | 0 |
| 14 | 2 | 0 | 0 |
| 15 | 1 | 0 | 0 |
| 16-22 | 0 | 0 | 0 |

### The Driver Draft
To keep the league competitive, we utilize a dynamic drafting order for every round:
* **Draft Order:** Drivers are drafted from **worst performer to best performer** based on the results of the previous race round.
* **Multi-Event Driver Selection:** Once a driver is drafted for a round, they are your designated point-earner for **both the Sprint (if applicable) and the Grand Prix.**

---

## Architecture

This project utilizes a modern "Data-as-Code" stack to power the league:

* **Scoring Engine:** Python scripts managed by `uv` that ingest race data and apply the custom scoring logic defined above.
* **Data Warehouse:** **AWS S3** stores the historical "Picks" and "Results" as optimized Parquet files.
* **Analytics Layer:** [Evidence.dev](https://evidence.dev), a markdown-based BI tool that uses SQL to generate the leaderboard directly from the data lake.
* **Automation:** A unified GitHub Actions workflow that executes the "Race-to-Rankings" process.

---

## Project Structure

```text
├── .github/workflows/    # CI/CD: The "League Commissioner" automation
├── pipeline/             # Python scoring logic (API pulls, Scoring, S3 uploads)
├── pages/                # Evidence.md files (The Scoreboard UI)
├── queries/              # SQL queries for leaderboards and driver stats
├── sources/              # S3 Connection configuration
├── pyproject.toml        # Python dependencies (managed by uv)
└── evidence.config.yaml  # Dashboard branding and navigation

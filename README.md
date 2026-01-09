# 🏎️ Drive to Survive: F1 Fantasy Scoreboard

[![F1 ETL and Dashboard Deploy](https://github.com/greglenane/drive-to-survive/actions/workflows/deploy.yml/badge.svg)](https://github.com/greglenane/drive-to-survive/actions/workflows/deploy.yml)

An automated fantasy league engine and analytics dashboard for Formula 1. This project handles the end-to-end lifecycle of a fantasy season: from extracting live race results to calculating league standings and visualizing performance trends.

## 🚀 Live Scoreboard
**View the standings here:** [https://greglenane.github.io/drive-to-survive/](https://greglenane.github.io/drive-to-survive/)

---

## 🏁 The Mission
The goal of this project is to eliminate the manual overhead of managing an F1 fantasy league. By combining an automated ETL pipeline with a high-performance dashboard, league members can see updated scores, driver efficiency, and constructor impact immediately following a race weekend.

---

## 🛠️ Architecture

This project utilizes a modern "Data-as-Code" stack to power the league:

* **Scoring Engine:** Python scripts managed by `uv` that ingest race data and apply custom league scoring logic.
* **Data Warehouse:** **AWS S3** stores the historical "Picks" and "Results" as optimized Parquet files.
* **Analytics Layer:** [Evidence.dev](https://evidence.dev), a markdown-based BI tool that uses SQL to generate the leaderboard directly from the data lake.
* **Automation:** A unified GitHub Actions workflow that executes the "Race-to-Rankings" process.



---

## 📂 Project Structure

```text
├── .github/workflows/    # CI/CD: The "League Commissioner" automation
├── pipeline/             # Python scoring logic (API pulls, Scoring, S3 uploads)
├── pages/                # Evidence.md files (The Scoreboard UI)
├── queries/              # SQL queries for leaderboards and driver stats
├── sources/              # S3 Connection configuration
├── pyproject.toml        # Python dependencies (managed by uv)
└── evidence.config.yaml  # Dashboard branding and navigation

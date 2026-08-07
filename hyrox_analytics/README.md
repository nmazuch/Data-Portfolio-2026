#  HYROX NYC 2026 — Race Performance Analytics

## Project Overview

This project presents an end-to-end data analytics pipeline built to analyze athlete performance during the HYROX NYC 2026 competition.

The main goal was to collect race results data, transform raw event data into structured relational datasets, analyze performance drivers, and build interactive dashboards to explore athlete results across divisions, genders, and age categories.

The project covers the complete data workflow:

**Data Extraction → Data Transformation → Data Modeling → Exploratory Analysis → Business Intelligence Dashboard**

---

#  Solution Architecture

```
HYROX Results Source
        │
        ▼
Automated Data Extraction (n8n workflow)
        │
        ▼
Relational Data Model
(PostgreSQL)
        │
        ▼
Data Cleaning & Transformation
(Python / Marimo)
        │
        ├───────────────┐
        ▼               ▼
Python Analysis     Power BI Dashboard
(statistical        (interactive
analysis)           reporting)
```

---

# Technologies Used

* **Python** — data processing, exploratory analysis, statistical calculations
* **Marimo** — interactive Python notebooks
* **PostgreSQL** — relational data modeling and storage
* **n8n** — automated data extraction workflow
* **Power BI** — interactive dashboards and performance reporting


---

# Data Pipeline

## 1. Data Extraction

An automated n8n workflow was created to collect HYROX race data.

The workflow includes:

* automated requests to race result endpoints,
* pagination handling,
* extraction of structured and semi-structured response data,
* transformation of raw results into analytical datasets.

Collected data includes:

* athlete information,
* race categories,
* final results,
* workout station splits,
* running lap splits,
* race replay timing data.

---

## 2. Data Modeling

Raw race data was transformed into a relational database structure consisting of 6 core tables:

| Table                | Description                                   |
| -------------------- | --------------------------------------------- |
| `events`             | Race event and division information           |
| `athletes`           | Athlete profiles and country information      |
| `results`            | Final race results, rankings and finish times |
| `result_members`     | Relationship between athletes and results     |
| `workout_splits`     | Station and running split performance         |
| `race_replay_splits` | Detailed race timing information              |

Database model:

```
events
   |
results
   |
result_members
   |
athletes


results
   |
workout_splits

results
   |
race_replay_splits
```

---

# Exploratory Data Analysis

Python analysis focused on identifying factors influencing HYROX performance.

Performed analyses:

* correlation analysis between station times and final ranking,
* comparison of OPEN vs PRO divisions,
* pacing analysis across running laps,
* fatigue pattern identification,
* station-level performance analysis.

---

# Key Findings

## 1. Running Performance as the Main Performance Driver

Running pace showed the strongest relationship with overall ranking.

* OPEN division:

  * Running correlation with rank: **r = 0.93**
  * Burpee Broad Jump and transition efficiency were also strong contributors.

* PRO division:

  * Running remained critical, but every workout station had a meaningful impact on final ranking.

---

## 2. Station Performance Differences Between OPEN and PRO

Analysis showed that heavier PRO weights do not always translate into a competitive advantage.

Sled Push and Sled Pull performance differences were influenced by increased loads, resulting in comparable or higher station times compared with OPEN athletes.

---

## 3. Fatigue and Pacing Patterns

The analysis identified different fatigue behaviors:

* Men showed a more consistent decline in running pace throughout the race.
* Women showed stronger pace changes after high-load stations.

A common pacing pattern was identified:

* Lap 2 was often the fastest running lap,
* potentially causing early fatigue accumulation later in the race.

---

# Power BI Dashboard

The Power BI report provides interactive analysis of:

* athlete performance,
* division comparison,
* gender analysis,
* age group performance,
* station-level results,
* ranking distributions.

Dashboard features:

* dynamic filtering,
* drill-through analysis,
* performance comparison.

---

#  Repository Structure

```
hyrox-nyc-2026-analytics/

│
├── data/
│   ├── athletes.csv
│   ├── events.csv
│   ├── race_replay_splits.csv
│   ├── result_members.csv
│   ├── results.csv
│   └── workout_splits.csv
│
├── workflows/
│   └── Hyrox_NY_2026_Full_Scraper.json
│
├── notebooks/
│   └── notebook.py
│
├── dashboards/
│   └── HYROX_Performance_Report.pbix
│
└── README.md
```

---

# Running the Project

## Requirements

* Python 3.10+
* Power BI Desktop
* PostgreSQL (optional, for database recreation)
* n8n (optional, for rerunning extraction workflow)

## Install Python dependencies

```bash
pip install pandas matplotlib plotly marimo
```

## Run analysis

```bash
marimo edit notebooks/notebook.py
```

Open the Power BI report:

```
dashboards/HYROX_Performance_Report.pbix
```

---

# Author

Natalia


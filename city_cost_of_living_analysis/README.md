# Poland Salary & Cost of Living Analysis (2010–2024)

An exploratory data analysis notebook (built with [marimo](https://marimo.io)) examining how salaries and the cost of living have evolved across Polish cities between 2010 and 2024.

## Dataset

`poland_col_salary_longitudinal_2010_2024.csv` — 2,745 rows covering **180 cities** across all **16 Polish voivodeships**, from 2010 to 2024.

| Column | Description |
|---|---|
| `year` | Reference year (2010–2024) |
| `city` | City or powiat seat name (Polish spelling) |
| `voivodeship` | One of 16 Polish administrative provinces |
| `city_tier` | Size category: `metropolis`, `city_large`, `city_medium`, `city_small`, `town`, `small_town` |
| `population_approx` | Approximate urban population |
| `avg_salary_gross_pln` | Average monthly gross salary (PLN) |
| `median_salary_gross_pln` | Estimated median gross salary (≈76% of average, per GUS) |
| `median_salary_net_pln` | Estimated take-home net salary (≈71.8% of gross, standard employment contract) |
| `national_avg_salary_gross_pln` | GUS national average for that year, used as a benchmark |
| `national_min_wage_pln` | Official minimum wage (Dz.U.) |
| `salary_to_national_ratio` | City salary ÷ national average — tracks regional convergence |
| `cpi_annual_pct` | Poland's annual CPI inflation rate (GUS/World Bank) |
| `cost_of_living_index` | Relative cost-of-living index (Warsaw = 100), Numbeo-derived |
| `rent_1br_city_center_pln` | Monthly rent, 1-bedroom apartment, city center (PLN) |
| `rent_1br_outside_center_pln` | Monthly rent, 1-bedroom, outside center (PLN) |
| `meal_cheap_restaurant_pln` | Inexpensive restaurant meal price (PLN) |
| `groceries_monthly_pln` | Estimated monthly grocery spend for one person (PLN) |
| `public_transport_monthly_pln` | Monthly public transport pass (PLN) |
| `est_monthly_cost_single_pln` | Total estimated monthly cost of living, single person (PLN) |
| `affordability_ratio` | `median_net_salary ÷ est_monthly_cost` |
| `rent_to_income_pct` | Rent (outside center) as % of gross salary |
| `data_source` | `numbeo` = direct Numbeo 2024 data; `gus_modeled` = GUS + tier model |

## What the notebook covers

1. **Data loading & cleaning** — loads the CSV, detects and drops duplicate rows, reports the resulting shape.
2. **Overview** — `shape`, random sample, `describe()`, and `info()` for a first look at the dataset.
3. **Univariate trend analysis** — tracks the yearly median of six key indicators over time:
   - average gross salary
   - median net salary
   - estimated monthly cost of living
   - affordability ratio
   - rent-to-income share
   - annual CPI inflation

   Shown both as **absolute trend lines** (median per year) and as an **indexed trend** (2010 = 100) to compare relative growth rates across metrics. A summary table ranks metrics by percentage change from 2010 to 2024.
4. **Distribution over time** — an interactive box plot (metric selectable via dropdown) showing how the spread of a chosen indicator across cities has changed year by year.
5. **Correlation analysis** — Pearson correlation matrix across all numeric columns, visualized as a heatmap, plus ranked tables of the strongest positive and negative correlations.
6. **Outlier detection** — applies the IQR rule (`Q1 - 1.5×IQR` / `Q3 + 1.5×IQR`) to every numeric column (excluding `year`), with:
   - a summary table of bounds and outlier counts per column,
   - a drill-down table of individual outlier observations by column,
   - a per-city summary of how many outlier points each city contributes.

## Tech stack

- **[marimo](https://marimo.io)** — reactive Python notebook (`analyze_salary.py`)
- **pandas** — data loading, cleaning, and aggregation
- **Altair** — interactive charts (line charts, box plots, heatmap)

## Files

- `analyze_salary.py` — the marimo notebook source (reactive Python cells)
- `analyze_salary.html` — a static, self-contained HTML export of the notebook for viewing without running marimo
- `poland_col_salary_longitudinal_2010_2024.csv` — the source dataset

## Running the notebook

```bash
pip install marimo pandas altair
marimo edit analyze_salary.py
```

By default the notebook reads the CSV from `/workspace/poland_col_salary_longitudinal_2010_2024.csv` — update the path in the data-loading cell if your file lives elsewhere, or place the CSV at that path.

To view the pre-rendered results without running Python, simply open `analyze_salary.html` in a browser.

## Notes / caveats

- `median_salary_gross_pln`, `median_salary_net_pln`, and parts of the cost-of-living figures are **modeled estimates** (fixed ratios applied to averages), not directly measured statistics — treat precision accordingly.
- Data for smaller cities in earlier years relies more heavily on the `gus_modeled` source rather than direct Numbeo observations; source composition should be checked before drawing strong conclusions about specific towns.


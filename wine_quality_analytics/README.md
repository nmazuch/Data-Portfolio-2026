# Wine Quality Analytics

A Power BI dashboard for exploring the relationship between wine price and quality. The project uses the `winemag-data-130k-v2` dataset and focuses on price segmentation, market positioning, wine ratings, and identifying high-quality wines at relatively low prices.

> **Note:** The dashboard interface and visualizations are currently available in Polish. An English version of the report may be added in the future.


## Project overview

The dashboard helps analyze whether a higher wine price is associated with a higher rating. It also highlights market segments and potential value-for-money wines based on the relationship between price and score.

## Repository structure

```text
wine_quality_analytics/
├── data/
│   └── winemag-data-130k-v2/
└── dashboard/
    └── wine_quality_dashboard.pbix
```

- `data/winemag-data-130k-v2/` — source dataset used for the analysis.
- `dashboard/wine_quality_dashboard.pbix` — Power BI report file.

## Dashboard sections

### Quality analysis

Presents the relationship between wine price and rating, including average price, average score, price per point, and price segmentation.

### Market positioning

Classifies wines into four groups based on price and quality:

- **Hidden gems** — high quality at a relatively low price.
- **Premium** — high quality and high price.
- **Overpriced** — relatively high price without a corresponding quality level.
- **Low value** — an unfavorable relationship between price and quality.

### Exceptional deals

Highlights wines that combine high ratings with relatively low prices. Users can explore wine name, country of origin, price, score, and price-per-point value.

## Key insights

The report highlights the following observations:

- A significant share of wines offers high quality at a relatively low price.
- Increasing the price above a certain level does not necessarily result in a meaningful increase in rating.
- The relationship between price and score can be more useful than price alone when searching for good-value wines.

## How to use the report

1. Clone or download this repository.
2. Open `dashboard/wine_quality_dashboard.pbix` in Power BI Desktop.
3. If necessary, update the data-source path to the local `data/winemag-data-130k-v2/` folder.
4. Refresh the data in Power BI Desktop.
5. Use the report tabs and filters to explore the analysis.

## Technologies

- Power BI Desktop
- Data analysis and visualization
- Wine review data analysis

## Data source

The project is based on the `winemag-data-130k-v2` wine reviews dataset. The dataset contains information such as wine name, country of origin, price, variety, and reviewer score.

## Project purpose

This project was created as a data analytics and visualization portfolio project. Its purpose is to present an accessible analysis of wine quality, pricing, and value for money using an interactive Power BI dashboard.

import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pl
    import altair as alt

    return alt, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    * year - Reference year (2010–2024)

    * bcity - City or powiat seat name (Polish spelling)

    * voivodeship - One of 16 Polish administrative provincescity_tiermetropolis / city_large / *

    * city_medium / city_small / town / small_town

    * population_approx - Approximate urban population

    * avg_salary_gross_pln - Average monthly gross salary (PLN)

    * median_salary_gross_pln - Estimated median gross salary (≈ 76% of avg, per GUS)

    * median_salary_net_pln - Estimated take-home net salary (≈ 71.8% of gross, standard UoP contract)

    * national_avg_salary_gross_pln - GUS national average for that year useful as benchmarknational_min_wage_plnOfficial minimum wage (Dz.U.)

    * salary_to_national_ratio - City salary ÷ national average tracks regional convergence

    * cpi_annual_pct - Poland annual CPI inflation rate (GUS/World Bank)

    * cost_of_living_index - Relative CoL index (Warsaw = 100), Numbeo-derived

    * rent_1br_city_center_pln - Monthly rent, 1-bedroom apartment, city center (PLN)

    * rent_1br_outside_center_pln - Monthly rent, 1-bedroom, outside center (PLN)

    * meal_cheap_restaurant_pln - Inexpensive restaurant meal price (PLN)

    * groceries_monthly_pln - Estimated monthly grocery spend for 1 person (PLN)

    * public_transport_monthly_pln - Monthly public transport pass (PLN)

    * est_monthly_cost_single_pln - Total estimated monthly cost of living, single person (PLN)

    * affordability_ratio - median_net_salary ÷ est_monthly_cost

    * rent_to_income_pctRent (outside center) - as % of gross salary

    * data_source"numbeo" = direct Numbeo 2024 data; "gus_modeled" = GUS + tier model
    """)
    return


@app.cell
def _(pl):
    salary_df = pl.read_csv("/workspace/poland_col_salary_longitudinal_2010_2024.csv")
    duplicate_rows = salary_df.duplicated().sum()
    salary_df = salary_df.drop_duplicates().reset_index(drop=True)
    salary_df
    return duplicate_rows, salary_df


@app.cell
def _(duplicate_rows, mo, salary_df):
    mo.md(f"""
    Wczytano dane z pliku `/workspace/poland_col_salary_longitudinal_2010_2024.csv`.

    Liczba wykrytych duplikatów: **{duplicate_rows}**  
    Liczba wierszy po usunięciu duplikatów: **{salary_df.shape[0]}**  
    Liczba kolumn: **{salary_df.shape[1]}**
    """)
    return


@app.cell
def _(salary_df):
    salary_df.shape
    return


@app.cell
def _(salary_df):
    salary_df.sample(10)
    return


@app.cell
def _(salary_df):
    salary_df.describe()
    return


@app.cell
def _(salary_df):
    salary_df.info()
    return


@app.cell
def _(mo):
    mo.md(f"""
    # Analiza jednowymiarowa wybranych kolumn

    Do analizy wybrałem kolumny, które najlepiej pokazują zmianę sytuacji ekonomicznej miast w czasie:

    - **avg_salary_gross_pln** — pokazuje dynamikę przeciętnych wynagrodzeń,
    - **median_salary_net_pln** — lepiej opisuje typowy dochód „do ręki”,
    - **est_monthly_cost_single_pln** — obrazuje zmianę kosztów życia,
    - **affordability_ratio** — pokazuje relację dochodu do kosztów życia,
    - **rent_to_income_pct** — pozwala ocenić obciążenie czynszem,
    - **cpi_annual_pct** — pokazuje tempo inflacji.

    Dobrałem dwa typy wizualizacji:

    1. **wykresy liniowe** — do obserwacji trendu w kolejnych latach,
    2. **wykres pudełkowy** — do obserwacji, jak zmieniał się rozkład wartości między miastami.
    """)
    return


@app.cell
def _():
    analysis_metrics = {
        "Średnie wynagrodzenie brutto": "avg_salary_gross_pln",
        "Mediana wynagrodzenia netto": "median_salary_net_pln",
        "Szacowany miesięczny koszt życia": "est_monthly_cost_single_pln",
        "Wskaźnik dostępności": "affordability_ratio",
        "Udział czynszu w dochodzie": "rent_to_income_pct",
        "Inflacja CPI": "cpi_annual_pct",
    }
    analysis_labels = {value: key for key, value in analysis_metrics.items()}
    return analysis_labels, analysis_metrics


@app.cell
def _(analysis_labels, analysis_metrics, salary_df):
    yearly_median_wide = (
        salary_df.groupby("year")[list(analysis_metrics.values())]
        .median()
        .reset_index()
    )

    yearly_median_long = yearly_median_wide.melt(
        id_vars="year",
        var_name="metric",
        value_name="median_value",
    )
    yearly_median_long["metric_label"] = yearly_median_long["metric"].map(analysis_labels)

    analysis_change_summary = (
        yearly_median_long.sort_values("year")
        .groupby(["metric_label", "metric"], as_index=False)
        .agg(
            start_year=("year", "first"),
            end_year=("year", "last"),
            start_value=("median_value", "first"),
            end_value=("median_value", "last"),
        )
    )
    analysis_change_summary["abs_change"] = (
        analysis_change_summary["end_value"] - analysis_change_summary["start_value"]
    )
    analysis_change_summary["pct_change"] = (
        analysis_change_summary["abs_change"] / analysis_change_summary["start_value"] * 100
    )
    analysis_change_summary = analysis_change_summary[
        [
            "metric_label",
            "start_year",
            "start_value",
            "end_year",
            "end_value",
            "abs_change",
            "pct_change",
        ]
    ].sort_values("pct_change", ascending=False)

    analysis_change_summary
    return (yearly_median_long,)


@app.cell
def _(alt, analysis_metrics, yearly_median_long):
    analysis_trend_chart = (
        alt.Chart(yearly_median_long)
        .mark_line(point=True)
        .encode(
            x=alt.X("year:O", title="Rok"),
            y=alt.Y("median_value:Q", title="Mediana w danym roku"),
            tooltip=[
                alt.Tooltip("metric_label:N", title="Kolumna"),
                alt.Tooltip("year:O", title="Rok"),
                alt.Tooltip("median_value:Q", title="Wartość", format=",.2f"),
            ],
        )
        .properties(width=280, height=180, title="Zmiana mediany wybranych kolumn w czasie")
        .facet(
            facet=alt.Facet(
                "metric_label:N",
                sort=list(analysis_metrics.keys()),
                title="Kolumna",
            ),
            columns=2,
        )
        .resolve_scale(y="independent")
    )

    analysis_trend_chart
    return


@app.cell
def _(alt, analysis_metrics, yearly_median_long):
    yearly_index_long = yearly_median_long.copy()
    yearly_index_long["base_value"] = yearly_index_long.groupby("metric")["median_value"].transform("first")
    yearly_index_long["index_2010"] = (
        yearly_index_long["median_value"] / yearly_index_long["base_value"] * 100
    )

    yearly_index_chart = (
        alt.Chart(yearly_index_long)
        .mark_line(point=True)
        .encode(
            x=alt.X("year:O", title="Rok"),
            y=alt.Y("index_2010:Q", title="Indeks zmian (2010 = 100)"),
            tooltip=[
                alt.Tooltip("metric_label:N", title="Kolumna"),
                alt.Tooltip("year:O", title="Rok"),
                alt.Tooltip("index_2010:Q", title="Indeks", format=",.1f"),
            ],
            color=alt.Color("metric_label:N", legend=None),
        )
        .properties(width=280, height=180, title="Tempo zmian względem 2010 roku")
        .facet(
            facet=alt.Facet(
                "metric_label:N",
                sort=list(analysis_metrics.keys()),
                title="Kolumna",
            ),
            columns=2,
        )
    )

    yearly_index_chart
    return


@app.cell
def _(analysis_metrics, mo):
    analysis_metric_selector = mo.ui.dropdown(
        options=analysis_metrics,
        value="Mediana wynagrodzenia netto",
        label="Wybierz kolumnę do analizy rozkładu",
        full_width=True,
    )
    analysis_metric_selector
    return (analysis_metric_selector,)


@app.cell
def _(alt, analysis_labels, analysis_metric_selector, salary_df):
    analysis_distribution_df = salary_df[["year", analysis_metric_selector.value]].dropna().rename(
        columns={analysis_metric_selector.value: "metric_value"}
    )
    analysis_distribution_label = analysis_labels[analysis_metric_selector.value]

    analysis_distribution_chart = (
        alt.Chart(analysis_distribution_df)
        .mark_boxplot(size=18)
        .encode(
            x=alt.X("year:O", title="Rok"),
            y=alt.Y("metric_value:Q", title=analysis_distribution_label),
            color=alt.Color("year:O", legend=None),
        )
        .properties(
            width=800,
            height=380,
            title=f"Zmiana rozkładu w czasie: {analysis_distribution_label}",
        )
    )

    analysis_distribution_chart
    return


@app.cell
def _(mo):
    mo.md(f"""
    # Korelacje pomiędzy kolumnami numerycznymi

    Poniżej analizuję zależności między wszystkimi kolumnami numerycznymi przy użyciu współczynnika korelacji Pearsona.

    Interpretacja:
    - wartości bliskie **1** oznaczają silną dodatnią zależność,
    - wartości bliskie **-1** oznaczają silną ujemną zależność,
    - wartości bliskie **0** oznaczają słabą lub brak liniowej zależności.
    """)
    return


@app.cell
def _(salary_df):
    numeric_columns = salary_df.select_dtypes(include="number").columns.tolist()
    correlation_matrix_df = salary_df[numeric_columns].corr(numeric_only=True)

    correlation_long_df = (
        correlation_matrix_df
        .reset_index()
        .rename(columns={"index": "metric_x"})
        .melt(id_vars="metric_x", var_name="metric_y", value_name="correlation")
    )
    correlation_long_df = correlation_long_df[correlation_long_df["metric_x"] != correlation_long_df["metric_y"]].copy()
    correlation_long_df["pair_key"] = correlation_long_df.apply(
        lambda row: " | ".join(sorted([row["metric_x"], row["metric_y"]])),
        axis=1,
    )
    correlation_long_df["abs_correlation"] = correlation_long_df["correlation"].abs()

    correlation_pairs_df = (
        correlation_long_df
        .drop_duplicates(subset="pair_key")
        .sort_values("abs_correlation", ascending=False)
        [["metric_x", "metric_y", "correlation", "abs_correlation"]]
        .reset_index(drop=True)
    )

    correlation_pairs_df.head(20)
    return correlation_long_df, correlation_pairs_df, numeric_columns


@app.cell
def _(alt, correlation_long_df, numeric_columns):
    correlation_heatmap = (
        alt.Chart(correlation_long_df)
        .mark_rect()
        .encode(
            x=alt.X("metric_x:N", title="Kolumna", sort=numeric_columns),
            y=alt.Y("metric_y:N", title="Kolumna", sort=numeric_columns),
            color=alt.Color(
                "correlation:Q",
                title="Korelacja",
                scale=alt.Scale(domain=[-1, 0, 1], range=["#b2182b", "#f7f7f7", "#2166ac"]),
            ),
            tooltip=[
                alt.Tooltip("metric_x:N", title="Kolumna X"),
                alt.Tooltip("metric_y:N", title="Kolumna Y"),
                alt.Tooltip("correlation:Q", title="Korelacja", format=".3f"),
            ],
        )
        .properties(
            width=520,
            height=520,
            title="Macierz korelacji kolumn numerycznych",
        )
    )

    correlation_heatmap
    return


@app.cell
def _(correlation_pairs_df, mo):
    positive_correlation_pairs_df = (
        correlation_pairs_df[correlation_pairs_df["correlation"] > 0]
        .sort_values("correlation", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    negative_correlation_pairs_df = (
        correlation_pairs_df[correlation_pairs_df["correlation"] < 0]
        .sort_values("correlation", ascending=True)
        .head(10)
        .reset_index(drop=True)
    )

    mo.ui.tabs({
        "Najsilniejsze dodatnie": mo.ui.table(positive_correlation_pairs_df),
        "Najsilniejsze ujemne": mo.ui.table(negative_correlation_pairs_df),
    })
    return


@app.cell
def _(pl, salary_df):
    outlier_numeric_columns = [
        column
        for column in salary_df.select_dtypes(include="number").columns
        if column != "year"
    ]

    outlier_bounds_records = []
    outlier_value_records = []

    for outlier_column in outlier_numeric_columns:
        outlier_series = salary_df[outlier_column].dropna()
        outlier_q1 = outlier_series.quantile(0.25)
        outlier_q3 = outlier_series.quantile(0.75)
        outlier_iqr = outlier_q3 - outlier_q1
        outlier_lower_bound = outlier_q1 - 1.5 * outlier_iqr
        outlier_upper_bound = outlier_q3 + 1.5 * outlier_iqr

        outlier_mask = (
            salary_df[outlier_column].notna()
            & (
                (salary_df[outlier_column] < outlier_lower_bound)
                | (salary_df[outlier_column] > outlier_upper_bound)
            )
        )

        outlier_rows_for_column = salary_df.loc[
            outlier_mask,
            ["year", "city", "voivodeship", "city_tier", outlier_column],
        ].copy()

        outlier_bounds_records.append(
            {
                "column": outlier_column,
                "q1": outlier_q1,
                "q3": outlier_q3,
                "iqr": outlier_iqr,
                "lower_bound": outlier_lower_bound,
                "upper_bound": outlier_upper_bound,
                "outlier_count": int(outlier_mask.sum()),
                "outlier_share_pct": round(outlier_mask.mean() * 100, 2),
            }
        )

        for _, outlier_row in outlier_rows_for_column.iterrows():
            outlier_value_records.append(
                {
                    "column": outlier_column,
                    "year": outlier_row["year"],
                    "city": outlier_row["city"],
                    "voivodeship": outlier_row["voivodeship"],
                    "city_tier": outlier_row["city_tier"],
                    "outlier_value": outlier_row[outlier_column],
                }
            )

    outlier_bounds_df = (
        pl.DataFrame(outlier_bounds_records)
        .sort_values(["outlier_count", "column"], ascending=[False, True])
        .reset_index(drop=True)
    )
    outlier_values_df = (
        pl.DataFrame(outlier_value_records)
        .sort_values(["column", "year", "city", "outlier_value"])
        .reset_index(drop=True)
    )
    outlier_total_points = int(outlier_bounds_df["outlier_count"].sum())
    outlier_columns_with_values = int((outlier_bounds_df["outlier_count"] > 0).sum())

    outlier_bounds_df
    return outlier_bounds_df, outlier_values_df


@app.cell
def _(mo):
    mo.md(r"""
    # Wartości odstające w danych

    Do wykrywania wartości odstających użyłem reguły IQR:

    $$IQR = Q3 - Q1$$

    Za wartości odstające uznaję obserwacje mniejsze niż:

    $$Q1 - 1.5 \cdot IQR$$

    lub większe niż:

    $$Q3 + 1.5 \cdot IQR$$

    Przeanalizowano **{len(outlier_numeric_columns)}** kolumn liczbowych
    (z pominięciem kolumny **year** jako zmiennej czasowej).

    - Łączna liczba wykrytych wartości odstających: **{outlier_total_points}**
    - Liczba kolumn, w których występują wartości odstające: **{outlier_columns_with_values}**
    """)
    return


@app.cell
def _(mo, outlier_bounds_df):
    mo.ui.table(outlier_bounds_df)
    return


@app.cell
def _(mo, outlier_bounds_df):
    outlier_column_selector = mo.ui.dropdown(
        options=outlier_bounds_df["column"].tolist(),
        value=outlier_bounds_df.loc[outlier_bounds_df["outlier_count"].idxmax(), "column"]
        if not outlier_bounds_df.empty
        else None,
        label="Wybierz kolumnę, aby zobaczyć konkretne wartości odstające",
        full_width=True,
    )

    outlier_column_selector
    return (outlier_column_selector,)


@app.cell
def _(mo, outlier_column_selector, outlier_values_df):
    selected_outlier_values_df = (
        outlier_values_df[outlier_values_df["column"] == outlier_column_selector.value]
        .sort_values(["year", "city", "outlier_value"])
        .reset_index(drop=True)
    )

    mo.ui.table(selected_outlier_values_df)
    return


@app.cell
def _(mo, outlier_values_df):
    outlier_city_summary_df = (
        outlier_values_df.groupby("city", as_index=False)
        .size()
        .rename(columns={"size": "outlier_points"})
        .sort_values(["outlier_points", "city"], ascending=[False, True])
        .reset_index(drop=True)
    )

    mo.ui.table(outlier_city_summary_df.head(20))
    return


if __name__ == "__main__":
    app.run()

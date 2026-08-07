# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "psycopg2-binary==2.9.12",
#     "sqlalchemy==2.0.51",
# ]
# ///

import marimo

__generated_with = "0.23.9"
app = marimo.App(
    width="medium",
    css_file="/usr/local/_marimo/custom.css",
    auto_download=["html"],
)


@app.cell
def _():
    import pandas as pd
    import marimo as mo

    # 1. List of all source CSV files
    datasets_list = [
        'events', 
        'athletes', 
        'results',  
        'workout_splits', 
        'race_replay_splits',
        'result_members'
    ]

    # 2. Dictionary to store DataFrames loaded from local CSVs
    dataframes_dict = {}

    for table_name in datasets_list:
        # Loading local files safely offline
        dataframes_dict[table_name] = pd.read_csv(f"{table_name}.csv")

    # 3. Generating the interactive data profiling report
    report_sections = {}

    for table_name, df_table in dataframes_dict.items():
        rows_count, cols_count = df_table.shape

        # Creating column summary (checking data types and counting missing values)
        schema_info_df = pd.DataFrame({
            'Data Type': df_table.dtypes.astype(str),
            'Non-Null Count': df_table.notna().sum(),
            'Missing Values (Null)': df_table.isna().sum()
        }).reset_index().rename(columns={'index': 'Column Name'})

        # Creating interactive tabs for each data table
        tab_contents = mo.ui.tabs({
            "📊 Summary": mo.md(f"**Number of rows:** {rows_count} \n\n**Number of columns:** {cols_count}"),
            "🛠️ Schema & Nulls": mo.ui.table(schema_info_df),
            "👀 Data Preview": mo.ui.table(df_table.head(10))
        })

        # Appending to the main accordion structure
        report_sections[f"🗄️ Table: {table_name}"] = tab_contents

    # 4. Render the final report as an interactive Accordion dropdown
    mo.accordion(report_sections)
    return dataframes_dict, mo, pd


@app.cell
def _(dataframes_dict, mo, pd):
    def get_clean_stats(df_input):
        cols_to_drop = ['id', 'result_id', 'athlete_id', 'event_id']
        df_clean = df_input.drop(columns=[c for c in cols_to_drop if c in df_input.columns])

        # Extract only numerical columns to calculate statistics
        df_numeric = df_clean.select_dtypes(include=['number'])

        if df_numeric.empty:
            return None

        # Calculate basic descriptive statistics
        stats_df = df_numeric.describe().loc[['mean', '50%', 'std', 'min', 'max']].T

        # Rename columns to clean English equivalents
        stats_df = stats_df.rename(columns={
            '50%': 'median', 
            'mean': 'mean', 
            'std': 'std_dev', 
            'min': 'min', 
            'max': 'max'
        })
        return stats_df

    # 2. Executing the function using our new dictionary naming

    # Fetching the 'results' table from our updated dictionary
    df_results_copy = dataframes_dict['results'].copy()

    # Convert time format to total seconds for statistical calculations
    if 'overall_time' in df_results_copy.columns:
        df_results_copy['overall_seconds'] = pd.to_timedelta(df_results_copy['overall_time']).dt.total_seconds()

    # Generate the statistics table
    results_summary_stats = get_clean_stats(df_results_copy)

    # Display the interactive table in Marimo
    mo.ui.table(results_summary_stats)
    return


@app.cell
def _(dataframes_dict, mo, pd):
    # 1. Convert time to seconds (a crucial step for quantitative analysis!)
    # Extracting the 'results' table from our main dictionary
    df_results = dataframes_dict['results'].copy()

    # Convert 'overall_time' to timedelta, then to total seconds for statistical math
    df_results['overall_seconds'] = pd.to_timedelta(df_results['overall_time']).dt.total_seconds()

    # 2. Statistical calculations focusing purely on overall race time
    overall_time_stats = df_results['overall_seconds'].agg(['mean', 'median', 'std', 'min', 'max']).round(0)

    # 3. Create a clean, formatted DataFrame for the statistics overview
    df_time_stats_overview = pd.DataFrame(overall_time_stats).T 
    df_time_stats_overview.columns = ['Mean', 'Median', 'Std Dev', 'Min', 'Max']

    # 4. Determine distribution skewness dynamically
    skewness_text = (
        "a right-skewed distribution (indicating the presence of amateurs taking significantly longer to finish)" 
        if overall_time_stats['mean'] > overall_time_stats['median'] 
        else "a relatively even distribution of results"
    )

    # 5. Display the table and the analytical interpretation in Marimo
    mo.vstack([
        mo.ui.table(df_time_stats_overview),
        mo.md(f"""
        **Interpretation:** The average athlete finish time is approximately **{int(overall_time_stats['mean']/60)} minutes**. 

        Comparing the mean ({int(overall_time_stats['mean'])}s) to the median ({int(overall_time_stats['median'])}s) 
        indicates {skewness_text}.
        """)
    ])
    return (df_results,)


@app.cell
def _(df_results):
    import matplotlib.pyplot as plt

    # This will draw a histogram to visually show the distribution skewness
    # Divide total seconds by 60 to plot the time in minutes for better readability
    (df_results['overall_seconds'] / 60).plot.hist(bins=30, color='skyblue', edgecolor='black')

    # Add clean English labels and title
    plt.xlabel('Finish Time (minutes)')
    plt.ylabel('Number of Athletes')
    plt.title('HYROX Finish Time Distribution')

    # Return the current figure so Marimo renders the plot automatically
    plt.gcf()
    return


@app.cell
def _(dataframes_dict, mo, pd):
    # Extracting the two most critical tables with unique variable names for this cell
    df_res_clean = dataframes_dict['results'].copy()
    df_splits_clean = dataframes_dict['workout_splits'].copy()

    # ==========================================
    # 1. CLEANING THE RESULTS TABLE
    # ==========================================
    # Drop columns that are 100% empty to save memory
    columns_to_drop = [col for col in ['disqual_reason', 'info'] if col in df_res_clean.columns]
    if columns_to_drop:
        df_res_clean = df_res_clean.drop(columns=columns_to_drop)

    # Fill empty penalties and bonuses (assuming NaN means zero penalty/bonus)
    if 'penalty' in df_res_clean.columns:
        df_res_clean['penalty'] = df_res_clean['penalty'].fillna(pd.Timedelta(seconds=0))
    if 'bonus' in df_res_clean.columns:
        df_res_clean['bonus'] = df_res_clean['bonus'].fillna(pd.Timedelta(seconds=0))

    # ==========================================
    # 2. CLEANING THE WORKOUT SPLITS TABLE
    # ==========================================
    # Drop rows where station time is missing (e.g., DNF - Did Not Finish athletes)
    df_splits_clean = df_splits_clean.dropna(subset=['split_time'])

    # Convert station time format to total seconds (float) for statistical calculations and plotting
    df_splits_clean['split_time_sec'] = pd.to_timedelta(df_splits_clean['split_time']).dt.total_seconds()

    # ==========================================
    # 3. MERGING AND PIVOTING DATA
    # ==========================================
    # Merge athlete result data with their specific station split times
    df_merged_full = pd.merge(df_res_clean, df_splits_clean, on='result_id', how='inner')

    # Pivot the table from 'long' format to 'wide' format
    # Each row represents one athlete, each column represents a specific station/run time
    df_pivot_wide = df_merged_full.pivot_table(
        index=['result_id', 'event_id', 'sex', 'age_group', 'rank_overall', 'overall_time'],
        columns='split_name',
        values='split_time_sec',
        aggfunc='first'
    ).reset_index()

    # Convert overall race time to seconds for quantitative analysis
    df_pivot_wide['overall_time_sec'] = pd.to_timedelta(df_pivot_wide['overall_time']).dt.total_seconds()

    # Display the beautifully structured wide dataset in Marimo
    mo.ui.table(df_pivot_wide.head(20))
    return (df_pivot_wide,)


@app.cell
def _(dataframes_dict, df_pivot_wide, mo, pd):
    # Fetch the 'events' table to extract division information (Pro/Open)
    df_events_clean = dataframes_dict['events'].copy()

    # 1. Merge the division data into our existing wide pivot table
    df_analytical_base = pd.merge(
        df_pivot_wide, 
        df_events_clean[['event_id', 'division']], 
        on='event_id', 
        how='left'
    )

    # 2. Create a primary category for charts (e.g., "PRO W", "OPEN M")
    # We search for the word 'PRO' in the division name, then append the gender from the 'sex' column
    df_analytical_base['Category'] = df_analytical_base['division'].apply(
        lambda x: 'PRO' if 'PRO' in str(x).upper() else 'OPEN'
    ) + ' ' + df_analytical_base['sex']

    # Display a preview of the final analytical table
    mo.ui.table(df_analytical_base.head(20))
    return (df_analytical_base,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Analysis 1: The "Heavy Sled" Myth vs. The Wall Balls "Wall" (Gender Split)

    **Context:**
    A common myth among amateur athletes is that a lack of brute strength (specifically on the Sled Push and Pull stations) is the primary barrier separating the OPEN division from PRO. We want to investigate at which stations PRO athletes actually build their biggest advantage over OPEN competitors, and whether this dynamic differs between genders.

    **Research Hypotheses:**
    * **H0 (Null Hypothesis):** There is no difference in pacing structure – regardless of gender, the OPEN category loses proportionally the same amount of time to PRO on strength stations (Sleds) as on endurance stations at the end of the race (Wall Balls).
    * **H1 (Alternative Hypothesis):** The pacing profile differs significantly depending on the race stage and gender. For men, the biggest critical point is endurance at the end (Wall Balls), while for women, the primary barrier to entering PRO is the significant jump in sled weight.

    **Methodology:**
    We will compare the average completion times for individual stations (1-8) between PRO and OPEN categories by generating two side-by-side radar charts (one for Men, one for Women).
    """)
    return


@app.cell
def _(df_analytical_base, mo):
    import plotly.express as px

    # 1. Define the 8 HYROX stations in chronological order
    station_columns = [
        '1000m SkiErg', '50m Sled Push', '50m Sled Pull', '80m Burpee Broad Jump', 
        '1000m Row', '200m Farmers Carry', '100m Sandbag Lunges', 'Wall Balls'
    ]

    # 2. Calculate average times for each category across all stations
    df_avg_times = df_analytical_base.groupby('Category')[station_columns].mean().reset_index()

    # 3. Pivot (melt) the dataframe for Plotly Express radar chart compatibility
    df_radar_melted = df_avg_times.melt(
        id_vars='Category', 
        value_vars=station_columns, 
        var_name='Station', 
        value_name='Average Time (sec)'
    )

    # 4. Filter data by gender for side-by-side comparison
    df_radar_men = df_radar_melted[df_radar_melted['Category'].isin(['PRO M', 'OPEN M'])]
    df_radar_women = df_radar_melted[df_radar_melted['Category'].isin(['PRO W', 'OPEN W'])]

    # 5. Create the Men's radar chart with unit suffixes
    fig_men = px.line_polar(
        df_radar_men, r='Average Time (sec)', theta='Station', color='Category',
        line_close=True, title='Critical Points (Men)',
        markers=True, color_discrete_sequence=['#ff004f', '#00b4d8']
    )
    fig_men.update_traces(fill='toself', opacity=0.5)
    fig_men.update_layout(polar=dict(radialaxis=dict(ticksuffix=" s", angle=0)))

    # 6. Create the Women's radar chart with unit suffixes
    fig_women = px.line_polar(
        df_radar_women, r='Average Time (sec)', theta='Station', color='Category',
        line_close=True, title='Critical Points (Women)',
        markers=True, color_discrete_sequence=['#ff004f', '#00b4d8']
    )
    fig_women.update_traces(fill='toself', opacity=0.5)
    fig_women.update_layout(polar=dict(radialaxis=dict(ticksuffix=" s", angle=0)))

    # 7. Display both charts side-by-side using Marimo's layout capabilities
    mo.hstack([fig_men, fig_women], justify="space-around")
    return (px,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Analysis Conclusions: The Fall of the "Sled Myth" and the Truth About Wall Balls

    Our initial hypothesis assumed that PRO athletes outclass amateurs on strength stations, and that the OPEN category loses the most time by hitting a "wall" at the end of the race. The data from HYROX NYC 2026 completely debunks this myth, revealing a **fascinating, entirely opposite dynamic**.

    Here are the 3 key takeaways derived from our radar charts:

    ### 1. The Wall Balls "Wall" Illusion
    * **Observation:** The time spent on the final station (Wall Balls) is **nearly identical** for both PRO and OPEN categories—the lines for both divisions practically overlap there.
    * **Conclusion:** The "wall" at the end of the race definitely exists, but everyone hits it equally, regardless of their advancement level. The tremendous endurance of PRO athletes only allows them to neutralize the heavier ball weight (9 kg vs 6 kg for men, 6 kg vs 4 kg for women), but it does not allow them to build a time advantage at this specific stage.

    ### 2. Sled Push is a Ruthless Validator (Especially for Women!)
    * **Observation:** This is where the charts diverge the most! Instead of pulling away from the amateurs, the PRO category spends **significantly more time** pushing the sled. For men, this loss is about 100 seconds. However, for women, we see an absolute chasm—PRO female athletes push the sled almost **twice as long** (~300 seconds) compared to OPEN females (~150 seconds).
    * **Conclusion:** The brutal jump in sled weight (175 kg in PRO M and 125 kg in PRO W) is the race's largest physiological barrier. For women planning to advance to the PRO division, pushing strength—not aerobic capacity—is the number one critical point.

    ### 3. So, Where Does the PRO Elite Actually Win the Race?
    * **Observation:** If the PRO category is losing minutes on the sleds, where do they make up the time? The radar shows a clear "pulling in" of PRO times toward the center of the chart on stations like **Burpee Broad Jump, Rowing, and Farmers Carry**.
    * **Conclusion:** Advancing to PRO and achieving great times does not rely on an advantage in absolute strength. The real difference is made by **dynamics, lung capacity, and lactic acid tolerance**. Wherever the weight increase is minimal, the elite makes up for the sled losses, outclassing amateurs with pure pace and cardiovascular endurance.
    """)
    return


@app.cell
def _(df_analytical_base, px):
    #import plotly.express as px

    # 1. Select the 5 critical stations for variance analysis
    boxplot_stations = [
        '50m Sled Push', '50m Sled Pull', 
        '80m Burpee Broad Jump', '200m Farmers Carry', 
        'Wall Balls'
    ]

    # 2. Extract necessary columns from the main analytical table
    df_boxplot_data = df_analytical_base[['Category'] + boxplot_stations].copy()

    # 3. Melt the dataframe from wide to long format for Plotly Express
    df_boxplot_melted = df_boxplot_data.melt(
        id_vars='Category',
        value_vars=boxplot_stations,
        var_name='Station',
        value_name='Time (seconds)'
    )

    # Remove system anomalies/outliers (times over 30 minutes on a single station)
    df_boxplot_melted = df_boxplot_melted[df_boxplot_melted['Time (seconds)'] < 1800]

    # 4. Draw the boxplots
    # Use facet_col_wrap=3 to arrange the 5 plots in a grid (3 on top, 2 on the bottom)
    fig_boxplots = px.box(
        df_boxplot_melted,
        x='Time (seconds)',
        y='Category',
        color='Category',
        facet_col='Station', 
        facet_col_wrap=3, 
        title='Data Dispersion: Analysis of 5 Critical Stations',
        color_discrete_map={
            'PRO M': '#00b4d8', 
            'OPEN M': '#90e0ef', 
            'PRO W': '#ff004f', 
            'OPEN W': '#ff8fa3'
        },
        orientation='h' 
    )

    # 5. Chart aesthetics
    # Unlink X axes (matches=None) so each station has its own perfectly adjusted scale
    fig_boxplots.update_xaxes(matches=None, ticksuffix=" s")

    # Update layout to increase chart height and accommodate the two rows
    fig_boxplots.update_layout(
        showlegend=False, 
        height=750, 
        margin=dict(l=20, r=20, t=60, b=20) 
    )

    # 6. Display the figure
    fig_boxplots
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Variance Analysis Conclusions: The Truth Lies in the Spread

    Filtering out measurement errors (system anomalies over 30 minutes) allowed us to look at the true distribution of power in HYROX. The boxplots prove that the arithmetic mean hides the most important details of the race.

    Here are 4 brutal truths about athlete physiology exposed by our data:

    ### 1. Sled Push & Pull: The Elite's Critical Point (Especially for Women!)
    * Look at the boxes for the PRO category (especially **PRO W**) on the sled stations. Paradoxically, they are wider and shifted to the right compared to the OPEN category.
    * **Conclusion:** This is ultimate proof that the imposed weight (175 kg for men, 125 kg for women in the PRO division) is a massive barrier. The PRO category, which is usually highly compact, shows significant data dispersion here. Some athletes handle this weight smoothly, while for others, it is a true fight for survival.

    ### 2. Burpee Broad Jump: The Aerobic Chasm
    * There is no external weight on this station; it relies purely on aerobic capacity and dynamics. The results? The PRO category features narrow, tight boxes shifted far to the left (they execute this exercise like machines, at a very similar, fast pace).
    * Conversely, among amateurs (OPEN M and OPEN W), we see massive stretching of the boxes and an endless trail of "dots" (outliers).
    * **Conclusion:** It is the lack of an aerobic base, not a lack of strength, that differentiates amateurs the most and generates their biggest time losses in the middle of the race.

    ### 3. Farmers Carry: Forearm Devastation
    * Similar to the sleds, the weight jump in PRO (e.g., from 2x16 kg to 2x24 kg for women) takes its toll. The PRO W box is unusually wide compared to OPEN W.
    * **Conclusion:** Grip is the element that gives out the fastest. PRO female athletes often have to put the kettlebells down here, which drastically increases the time variance in this group.

    ### 4. Wall Balls: Everyone Hits the Wall, But Amateurs Stay There
    * The medians (the lines inside the boxes) for all four categories are very close to each other. But the real story is hidden in the "tail" on the right!
    * The tail of dots (outliers) for OPEN athletes stretches endlessly, reaching values of 1000–1500 seconds (over 15-25 minutes!).
    * **Conclusion:** Fatigue on the final station catches up to everyone. However, what separates the elite from amateurs is the **ability to recover between sets**. A PRO athlete will drop the ball, take two breaths, and keep throwing. An amateur needs long minutes to lower their heart rate, which drastically increases their time on the station.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### In-Depth Analysis: Does the Winning Formula Change in PRO?

    **Context:**
    The correlation analysis for the entire population showed us general trends, but it hides a crucial detail. The environment of the OPEN category differs drastically from the PRO elite. Since PRO athletes are physiologically much more evenly matched (especially regarding their aerobic base), the deciding factor for winning in this division might lie somewhere else entirely.

    **Hypothesis:**
    In the OPEN category, the overall result is primarily determined by pure aerobic capacity (Run Total, Burpees). In the PRO category, where the running pace is highly uniform, the key differentiators become the strictly strength-based stations (Sled Push) and flawless transitions (Roxzone).

    **Methodology:**
    We will split our dataset into two groups (PRO and OPEN) and generate two separate correlation matrices to compare the "mathematical formula for success" for amateurs versus the elite.
    """)
    return


@app.cell
def _(df_analytical_base, mo, px):
    #import plotly.express as px

    # 0. DEFINE VARIABLES AND CLEAN DATA
    # Filter out measurement errors/outliers (times over 30 min) on the Wall Balls station
    df_clean_corr = df_analytical_base[df_analytical_base['Wall Balls'] < 1800].copy()

    # Select the specific columns we want to analyze
    correlation_columns = [
        'overall_time_sec', 'Run Total', 'Roxzone Time', 
        '1000m SkiErg', '50m Sled Push', '50m Sled Pull', 
        '80m Burpee Broad Jump', '1000m Row', '200m Farmers Carry', 
        '100m Sandbag Lunges', 'Wall Balls'
    ]

    # 1. Split the clean dataset into PRO and OPEN groups
    df_pro_division = df_clean_corr[df_clean_corr['Category'].str.contains('PRO')].copy()
    df_open_division = df_clean_corr[~df_clean_corr['Category'].str.contains('PRO')].copy()

    # 2. Calculate two separate correlation matrices
    corr_matrix_pro = df_pro_division[correlation_columns].corr()
    corr_matrix_open = df_open_division[correlation_columns].corr()

    # 3. Generate the Heatmap for the PRO division
    fig_heatmap_pro = px.imshow(
        corr_matrix_pro, text_auto=".2f", aspect="auto", 
        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title="Winning Formula: PRO Division"
    )
    fig_heatmap_pro.update_layout(height=650, width=650, margin=dict(l=10, r=10, t=50, b=100))
    fig_heatmap_pro.update_xaxes(tickangle=-45)

    # 4. Generate the Heatmap for the OPEN division
    fig_heatmap_open = px.imshow(
        corr_matrix_open, text_auto=".2f", aspect="auto", 
        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title="Winning Formula: OPEN Division"
    )
    fig_heatmap_open.update_layout(height=650, width=650, margin=dict(l=10, r=10, t=50, b=100))
    fig_heatmap_open.update_xaxes(tickangle=-45)

    # 5. Display both charts elegantly side-by-side using Marimo
    mo.hstack([fig_heatmap_open, fig_heatmap_pro], justify="space-around")
    return (df_clean_corr,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Heatmap Comparison Conclusions: Two Different Worlds of HYROX

    Splitting the data into PRO and OPEN divisions revealed a powerful conclusion: the winning formula changes drastically depending on who you are competing against. A glance at the top row (`overall_time_sec`) in both correlation matrices exposes the brutal truth about this sport.

    ### 1. OPEN Division: A Festival of Running and Endurance
    In the OPEN category, we see a very clear division between critical stations and those that mathematically "do not matter":
    * **It's all about oxygen:** The race is won by running pace (**0.95**), fast Burpees (**0.84**), and zero rest in the Roxzone (**0.80**).
    * **"Useless" stations:** Time spent on the SkiErg (**0.06**), Farmers Carry (**0.07**), or Sandbag Lunges (**0.29**) for amateurs practically does not correlate with the final result at all! The differences between athletes on these stations are so small (or distributed so randomly) that shaving off seconds here does not move you up the leaderboard.

    ### 2. PRO Division: ZERO Margin for Error
    Look at the top row in the PRO table—**it is entirely lit up in red!** This is an absolutely fascinating analytical phenomenon.
    * **Everything matters:** In the PRO elite, every single element of the race has a correlation above **0.71** (even the SkiErg jumped from 0.06 in OPEN to 0.71 in PRO, and Farmers Carry from 0.07 to 0.74!).
    * **Why does this happen?** The PRO elite is incredibly evenly matched in terms of endurance. Everyone runs fast, and no one walks in the Roxzone. When the aerobic base ceases to be the main differentiator, the race comes down to fractions of a second on every single station. In PRO, you cannot afford to have a "weak exercise"—stumbling on any strength station immediately throws you off the podium.

    ### 3. Roxzone: The Only Constant in Both Worlds
    In both divisions, the time spent in the transition zone maintains a massive correlation with the final result (OPEN: **0.80**, PRO: **0.83**). This is the ultimate proof for any coach designing a training plan: efficient transitions are the only element of the race guaranteed to improve a ranking position, regardless of the athlete's advancement level.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Final Segmentation: 4 Winning Formulas (Gender & Division)

    **Context:**
    Our previous split into the PRO and OPEN divisions revealed drastic differences, but it still masked the physiological disparities between genders. We know from the variance analysis that the sled weight increase hits women significantly harder than men.

    **Methodology:**
    We are breaking the data down into 4 distinct categories (PRO Men, PRO Women, OPEN Men, OPEN Women). We will create a grid of 4 separate correlation maps to provide precise, mathematically backed training guidelines tailored specifically to each target group.
    """)
    return


@app.cell
def _(df_clean_corr, mo, px):
    #import plotly.express as px

    # 0. Define columns (to ensure the cell is 100% independent)
    segmentation_cols = [
        'overall_time_sec', 'Run Total', 'Roxzone Time', 
        '1000m SkiErg', '50m Sled Push', '50m Sled Pull', 
        '80m Burpee Broad Jump', '1000m Row', '200m Farmers Carry', 
        '100m Sandbag Lunges', 'Wall Balls'
    ]

    # 1. Filter the data into 4 specific demographic categories
    # Using df_clean_corr from the previous cell to exclude outliers
    df_pro_men = df_clean_corr[df_clean_corr['Category'] == 'PRO M'].copy()
    df_pro_women = df_clean_corr[df_clean_corr['Category'] == 'PRO W'].copy()
    df_open_men = df_clean_corr[df_clean_corr['Category'] == 'OPEN M'].copy()
    df_open_women = df_clean_corr[df_clean_corr['Category'] == 'OPEN W'].copy()

    # 2. Helper function to draw standardized heatmaps
    def create_segmented_heatmap(df_subset, chart_title):
        fig = px.imshow(
            df_subset[segmentation_cols].corr(), 
            text_auto=".2f", aspect="auto", 
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            title=chart_title
        )
        # Reduce chart size so all 4 fit nicely on the screen
        fig.update_layout(height=500, width=500, margin=dict(l=10, r=10, t=50, b=100))
        fig.update_xaxes(tickangle=-45)
        return fig

    # 3. Generate the 4 correlation maps
    fig_pro_men = create_segmented_heatmap(df_pro_men, "Winning Formula: PRO Men")
    fig_pro_women = create_segmented_heatmap(df_pro_women, "Winning Formula: PRO Women")
    fig_open_men = create_segmented_heatmap(df_open_men, "Winning Formula: OPEN Men")
    fig_open_women = create_segmented_heatmap(df_open_women, "Winning Formula: OPEN Women")

    # 4. Arrange them in a 2x2 grid (Top row: PRO, Bottom row: OPEN)
    row_pro_charts = mo.hstack([fig_pro_men, fig_pro_women], justify="center")
    row_open_charts = mo.hstack([fig_open_men, fig_open_women], justify="center")

    # Display the final layout vertically
    mo.vstack([row_pro_charts, row_open_charts])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Full Segmentation Conclusions (Gender & Division): 4 Winning Formulas

    Breaking down the correlation matrix into 4 independent groups (PRO M, PRO W, OPEN M, OPEN W) proves that HYROX is essentially four completely different sports. By focusing on the top row (`overall_time_sec`), we uncover the "cheat codes" for each of these demographics.

    ### 1. OPEN Men: "Run, Do Burpees, and Survive"
    This is the most shocking of all the matrices. For male amateurs, certain stations can literally be ignored!
    * **A shocking lack of correlation:** Performance on the SkiErg (**0.02**), Farmers Carry (**0.04**), and Sandbag Lunges (**0.19**) has virtually **zero** impact on your final placement.
    * **Conclusion:** Men in the OPEN division waste valuable weeks trying to maximize their personal bests on the rower or SkiErg. The winning formula here is brutally simple: pure running (**0.93**), a killer pace on Burpees (**0.82**), and zero rest in the Roxzone (**0.82**). Everything else is just background noise.

    ### 2. OPEN Women: Sandbag Lunges as the Silent Killer
    Unlike the men, amateur women cannot afford to slack off on half of the stations.
    * **The Lunges Chasm:** Pay attention to the Sandbag Lunges station. For men, the correlation was a mere 0.19, whereas for women, it is a massive **0.79**! A similar trend is seen on the SkiErg (jumping from 0.02 for men to **0.66** for women).
    * **Conclusion:** Due to differences in muscle mass and absolute strength, exercises that are merely a "weighted walk" for OPEN men act as a powerful validator determining the finish line placement for women.

    ### 3. PRO Women: The Wall Balls "Wall of Tears"
    Our assumptions about the massive demands placed on the female elite are confirmed. The PRO W matrix glows the brightest red of them all.
    * **The final stretch decides everything:** The correlation of Wall Balls time with the final result is a staggering **0.87** (the highest metric for a single station across all 4 groups!).
    * **Conclusion:** Even if a PRO female athlete runs exceptionally well (**0.95**) and survives the heavy sleds, the fate of the medals is decided at the very last station (with the 6 kg ball). In the female elite, there is absolutely zero margin for error at the finish line.

    ### 4. PRO Men: A Race of Machines with No Weak Points
    In the male elite, the game is played for fractions of a second, which is perfectly visible on the heatmap. This is the most balanced division of all, where the rules of the game completely deviate from the OPEN category.
    * **The end of "free" stations:** Unlike OPEN M (where the SkiErg had a 0.02 correlation), in PRO M, **every single station has a correlation above 0.71!** This means an elite male athlete must be an absolutely complete competitor. There is no room to "wait out" a weaker exercise—stumbling on the rower or lunges immediately drops you down the rankings.
    * **Sled Pull is more critical than Sled Push:** This is a very interesting physiological phenomenon. Pulling the sled (`Sled Pull` = **0.81**) correlates stronger with the final result than pushing it (`Sled Push` = **0.74**). Pushing engages natural body weight and leg strength, which the elite handles relatively evenly. Conversely, pulling a thick rope is a brutal test of back strength, hamstrings, and grip—this is exactly where the biggest advantages are forged among top-tier men.
    * **The Roxzone decides the medals:** The correlation of time spent in the transition zone here is a massive **0.84** (higher than on the strength stations!). With the running and strength pace of the entire field being so astronomically evenly matched, it is the sprinting, tactically perfect transitions between zones—and not stopping for chalk—that serve as the ultimate detail separating first place from fourth.

    ### 5. The Unchanging Foundation for Everyone
    Regardless of which division and gender we analyze, two elements remain the absolute, untouchable foundation of HYROX:
    1. **Running (Run Total):** A correlation always above **0.93**. Without an outstanding running time, the podium is firmly closed.
    2. **Transition Zone (Roxzone):** A correlation between **0.77 and 0.84**. Fast, tactical transitions between stations remain the most "free" way to overtake hundreds of competitors.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Pacing Analysis: Women as the Queens of Crisis Management

    **Context:**
    HYROX is a brutal endurance test lasting anywhere from 60 to 90 minutes. One of the biggest mistakes amateurs make is "burning out" in the early kilometers and stations, which results in a drastic drop in pace during the second half of the race.

    **Hypothesis:**
    Women exhibit a significantly smaller pace drop-off (better pacing) over the distance compared to men. Men are more prone to letting their egos take over and "redlining" early on, whereas women demonstrate much higher tactical discipline.

    **Methodology:**
    The most objective metric of pacing in HYROX is the analysis of the 8 running laps (each exactly 1000 meters). We will construct a pace curve (Line Plot) by averaging the times of successive running splits for each category. A steep curve climbing upward indicates a drastic loss of energy. A flat, horizontal curve represents perfect pacing.
    """)
    return


@app.cell
def _(dataframes_dict, df_analytical_base, pd, px):


    # 1. Create NEW variables dedicated to the pacing plot to avoid Marimo redefinition errors
    df_pacing_splits = dataframes_dict['workout_splits'].copy()
    df_pacing_splits['split_name'] = df_pacing_splits['split_name'].astype(str).str.strip()

    # 2. Define the 8 running laps
    running_laps = [
        'Running 1', 'Running 2', 'Running 3', 'Running 4', 
        'Running 5', 'Running 6', 'Running 7', 'Running 8'
    ]

    # 3. Filter only the running splits and convert to seconds
    df_running_only = df_pacing_splits[df_pacing_splits['split_name'].isin(running_laps)].copy()
    df_running_only['run_sec'] = pd.to_timedelta(df_running_only['split_time']).dt.total_seconds()

    # 4. Pivot the data so each lap becomes a separate column
    df_running_pivot = df_running_only.pivot(
        index='result_id', 
        columns='split_name', 
        values='run_sec'
    ).reset_index()

    # 5. Merge with our main analytical base to get the demographics (Category)
    df_pacing_merged = pd.merge(
        df_analytical_base[['result_id', 'Category']], 
        df_running_pivot, 
        on='result_id', 
        how='inner'
    )

    # 6. Calculate average time per lap for each demographic category
    df_pacing_avg = df_pacing_merged.groupby('Category')[running_laps].mean().reset_index()

    # 7. Melt the dataframe back to long format for Plotly Line Chart compatibility
    df_pacing_melted = df_pacing_avg.melt(
        id_vars='Category', 
        value_vars=running_laps, 
        var_name='Lap', 
        value_name='Time (seconds)'
    )

    # 8. Draw the pacing curve
    fig_pacing = px.line(
        df_pacing_melted, 
        x='Lap', 
        y='Time (seconds)', 
        color='Category', 
        markers=True,
        title='Pacing Curve: Average Running Lap Times by Category',
        color_discrete_map={
            'PRO M': '#00b4d8',  # Dark blue
            'OPEN M': '#90e0ef', # Light blue
            'PRO W': '#ff004f',  # Dark pink/red
            'OPEN W': '#ff8fa3'  # Light pink
        }
    )

    # 9. Format the layout for better readability
    fig_pacing.update_yaxes(ticksuffix=" s")
    fig_pacing.update_layout(height=600, margin=dict(l=20, r=20, t=60, b=20))

    # 10. Display the plot seamlessly in Marimo
    fig_pacing
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Pacing Curve Conclusions: How the Elite Manages Crisis

    Analyzing the running pace across the 8 kilometers of a HYROX race sheds new light on pacing strategies. The pace curve isn't just a line—it's a record of the athlete's physiological "battle" with the strength stations.

    ### 1. The Second Kilometer Trap (Running 2)
    Across all four categories, we observe a clear, shared trend: `Running 2` is the fastest running split of the entire race.
    * **Conclusion:** This is the effect of "relief" after the first station (1000m SkiErg). Athletes subconsciously "open the throttle" on their pace, which is a **strategic mistake**. The sudden acceleration after the initial, heavy aerobic effort causes a subsequent pace "collapse" during `Running 3` (heading into the Sled Pull).

    ### 2. PRO M – The Definition of Masterful Pacing
    The dark blue line (PRO M) shows the least variance (so-called *pacing stability*).
    * **Conclusion:** The male elite can maintain an almost identical running pace even after the heaviest strength stations (Sled Push/Pull). This means that for PRO athletes, strength stations are not the "end of the effort" but merely a different form of it—their bodies exhibit an outstanding ability to rapidly clear lactic acid while running.

    ### 3. The "Sandbag Lunges" Hangover (Running 8)
    The spike in running time (drop in pace) on `Running 8` across all categories is massive. It's crucial to note that this final run happens right before the Wall Balls—meaning this exhaustion is the direct, devastating aftermath of Station 7 (**Sandbag Lunges**).
    * **Conclusion:** The time on `Running 8` is not a measure of running speed, but a **measure of fatigue resistance**. The biggest time loss relative to their own average pace is suffered by the `OPEN W` category, suggesting that for amateur women, the heavy lunges pose a significantly greater physiological challenge than for the other groups.

    ### Pacing vs. Physiology – The Truth Behind the "Jagged" Lines

    The pace analysis does not point to a conscious "energy-saving" strategy, but rather to two different models of fatigue:

    1. **The Male Model ("Fading" Strategy):** Men tend to show a linear degradation in running pace throughout the race. This stems from the fact that their initial pace is close to their maximum, and the accumulating fatigue after each station successively lowers their running capacity. This isn't "crisis management"; it's a slow depletion of resources.

    2. **The Female Model ("Fatigue Accumulation" Strategy):** The women's line is "jagged" because their running pace is more strongly dependent on the type of station just completed. When a station is highly taxing (e.g., sleds), the running pace drops drastically. When a station is less load-bearing (e.g., Burpees), the pace returns to normal. This shows that for women in HYROX, each station is a "separate challenge," whereas for men—especially in the OPEN category—the race is one long, accumulating oxygen debt.

    ### **The Verdict:** The optimal pacing model (which should be taught to amateurs) must aim to "flatten" the curve—eliminating the ego-driven sprint on `Running 2` in favor of a more stable, conservative pace that preserves energy for the critical final kilometer (`Running 8`).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Summary and Final Conclusions

    Our analysis of HYROX competition data allowed us to move beyond the intuitive feelings of coaches and examine the race through the lens of hard mathematics. Here are the most important takeaways that redefine how athletes should prepare for race day:

    ### 1. Shattering the Myth of a "Universal Race"
    HYROX is not a single, uniform sport.
    * **OPEN Division:** This is an endurance race—the running "engine" wins here.
    * **PRO Division:** This is a technical and strength race—any margin of error on a strength station has a colossal impact on the final placement.
    * **Conclusion:** A training plan for an OPEN athlete must look fundamentally different from one designed for a PRO athlete.

    ### 2. Physiology vs. Strategy (Pacing Verification)
    Our initial hypothesis regarding "better crisis management by women" proved incorrect, but it revealed something much more important. The Pacing Curves demonstrated that:
    * **Men** exhibit a tendency toward "strategic fading" (starting too fast, followed by a linear drop in pace).
    * **Women** exhibit a "reactive fatigue model"—their running pace is heavily dependent on the specific type of strength station they just completed.
    * **Conclusion:** Women do not necessarily need to learn "even running"; instead, training should focus on **faster heart rate recovery immediately following heavy strength stations**.

    ### 3. The Key to the Podium: Eliminating "Dead Zones"
    Thanks to the correlation heatmaps, we now know exactly where the hidden minutes lie:
    * **Roxzone:** These are the cheapest seconds you can gain in this sport.
    * **Sled Pull/Push & Wall Balls:** These are the ultimate "validators" in the PRO division, separating the podium finishers from the rest of the pack.
    * **SkiErg:** For amateurs, this is a station of low strategic importance. Dedicating the majority of training time to maximizing SkiErg performance is mathematically inefficient.
    """)
    return


if __name__ == "__main__":
    app.run()

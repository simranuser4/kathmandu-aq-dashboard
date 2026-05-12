import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(
    page_title="Kathmandu PM2.5 Dashboard",
    layout="wide"
)

st.title("Kathmandu PM2.5 Dashboard")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

df = pd.read_csv("clean_kathmandu_pm25.csv")
sensor_df = pd.read_csv("nepal_pm25_sensors.csv")

# CLEAN COLUMN NAMES
df.columns = df.columns.str.strip()
sensor_df.columns = sensor_df.columns.str.strip()

# ------------------------------------------------
# MERGE SENSOR INFO
# ------------------------------------------------

df = df.merge(
    sensor_df,
    on="sensor_id",
    how="left"
)

# ------------------------------------------------
# DATETIME FEATURES
# ------------------------------------------------

df["datetime"] = pd.to_datetime(df["datetime"])

df["date"] = df["datetime"].dt.date
df["day"] = df["datetime"].dt.day
df["hour"] = df["datetime"].dt.hour
df["month"] = df["datetime"].dt.month
df["year"] = df["datetime"].dt.year

# ------------------------------------------------
# LABELS
# ------------------------------------------------

hour_labels = {
    0: "12 AM",
    1: "1 AM",
    2: "2 AM",
    3: "3 AM",
    4: "4 AM",
    5: "5 AM",
    6: "6 AM",
    7: "7 AM",
    8: "8 AM",
    9: "9 AM",
    10: "10 AM",
    11: "11 AM",
    12: "12 PM",
    13: "1 PM",
    14: "2 PM",
    15: "3 PM",
    16: "4 PM",
    17: "5 PM",
    18: "6 PM",
    19: "7 PM",
    20: "8 PM",
    21: "9 PM",
    22: "10 PM",
    23: "11 PM"
}

month_labels = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

month_short = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}

# ------------------------------------------------
# KPI SECTION
# ------------------------------------------------

st.header("Dataset Information")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Records", len(df))

c2.metric(
    "Total Sensors",
    df["location_name"].nunique()
)

c3.metric(
    "Start Date",
    str(df["datetime"].min().date())
)

c4.metric(
    "End Date",
    str(df["datetime"].max().date())
)

# ------------------------------------------------
# LATEST PM2.5
# ------------------------------------------------

st.header("Latest Kathmandu PM2.5")

latest_time = df["datetime"].max()

latest_df = df[
    df["datetime"] == latest_time
]

sensor_latest = (
    latest_df
    .groupby("location_name")["pm25"]
    .mean()
    .reset_index()
)

latest_pm25 = sensor_latest["pm25"].mean()

if latest_pm25 <= 15:
    category = "Good"

elif latest_pm25 <= 35:
    category = "Moderate"

elif latest_pm25 <= 55:
    category = "Unhealthy for Sensitive Groups"

elif latest_pm25 <= 150:
    category = "Unhealthy"

else:
    category = "Hazardous"

a1, a2, a3 = st.columns(3)

a1.metric(
    "Latest PM2.5",
    round(latest_pm25, 2)
)

a2.metric(
    "AQ Category",
    category
)

a3.metric(
    "Sensors Reporting",
    len(sensor_latest)
)

# ------------------------------------------------
# SENSOR TABLE
# ------------------------------------------------

st.header("Latest Sensor Readings")

sensor_table = (
    latest_df
    .groupby("location_name")["pm25"]
    .mean()
    .reset_index()
    .sort_values("pm25", ascending=False)
)

st.dataframe(
    sensor_table,
    use_container_width=True
)

# ------------------------------------------------
# HOURLY TREND
# ------------------------------------------------

st.header("Hourly PM2.5 Trend")

available_dates = sorted(
    df["date"].unique()
)

selected_date = st.selectbox(
    "Select Date",
    available_dates,
    index=len(available_dates)-1,
    key="hourly_date"
)

hourly_df = df[
    df["date"] == selected_date
]

sensor_hourly = (
    hourly_df
    .groupby(["location_name", "hour"])["pm25"]
    .mean()
    .reset_index()
)

hourly_avg = (
    sensor_hourly
    .groupby("hour")["pm25"]
    .mean()
    .reset_index()
)

hourly_avg["hour_label"] = (
    hourly_avg["hour"]
    .map(hour_labels)
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=hourly_avg["hour_label"],
        y=hourly_avg["pm25"],
        mode="lines+markers",
        name="PM2.5"
    )
)

fig.add_hline(
    y=15,
    line_dash="dash",
    annotation_text="WHO Guideline"
)

fig.update_layout(
    title=f"Hourly PM2.5 Trend — {selected_date}",
    xaxis_title="Hour",
    yaxis_title="PM2.5 (µg/m³)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ------------------------------------------------
# AVERAGE TREND
# ------------------------------------------------

st.header("Average PM2.5 Trend")

trend_option = st.selectbox(
    "Trend Type",
    ["Monthly", "Yearly"],
    key="trend_option"
)

# ------------------------------------------------
# MONTHLY TREND
# ------------------------------------------------

if trend_option == "Monthly":

    years = sorted(df["year"].unique())

    selected_year = st.selectbox(
        "Select Year",
        years,
        index=len(years)-1,
        key="monthly_trend_year"
    )

    selected_month = st.selectbox(
        "Select Month",
        list(month_labels.keys()),
        format_func=lambda x: month_labels[x],
        key="monthly_trend_month"
    )

    month_df = df[
        (df["year"] == selected_year) &
        (df["month"] == selected_month)
    ]

    sensor_daily = (
        month_df
        .groupby(["location_name", "day"])["pm25"]
        .mean()
        .reset_index()
    )

    daily_avg = (
        sensor_daily
        .groupby("day")["pm25"]
        .mean()
        .reset_index()
    )

    all_days = pd.DataFrame({
        "day": range(1, 32)
    })

    daily_avg = all_days.merge(
        daily_avg,
        on="day",
        how="left"
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=daily_avg["day"],
            y=daily_avg["pm25"],
            mode="lines+markers",
            name="PM2.5"
        )
    )

    fig2.add_hline(
        y=15,
        line_dash="dash",
        annotation_text="WHO Guideline"
    )

    fig2.update_layout(
        title=f"Daily Average PM2.5 — {month_labels[selected_month]} {selected_year}",
        xaxis_title="Day",
        yaxis_title="PM2.5 (µg/m³)",
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ------------------------------------------------
# YEARLY TREND
# ------------------------------------------------

else:

    years = sorted(df["year"].unique())

    selected_year = st.selectbox(
        "Select Year for Yearly Trend",
        years,
        index=len(years)-1,
        key="yearly_trend_year"
    )

    year_df = df[
        df["year"] == selected_year
    ]

    sensor_monthly = (
        year_df
        .groupby(["location_name", "month"])["pm25"]
        .mean()
        .reset_index()
    )

    monthly_avg = (
        sensor_monthly
        .groupby("month")["pm25"]
        .mean()
        .reset_index()
    )

    all_months = pd.DataFrame({
        "month": range(1, 13)
    })

    monthly_avg = all_months.merge(
        monthly_avg,
        on="month",
        how="left"
    )

    monthly_avg["month_name"] = (
        monthly_avg["month"]
        .map(month_short)
    )

    fig3 = go.Figure()

    fig3.add_trace(
        go.Scatter(
            x=monthly_avg["month_name"],
            y=monthly_avg["pm25"],
            mode="lines+markers",
            name="PM2.5"
        )
    )

    fig3.add_hline(
        y=15,
        line_dash="dash",
        annotation_text="WHO Guideline"
    )

    fig3.update_layout(
        title=f"Monthly Average PM2.5 — {selected_year}",
        xaxis_title="Month",
        yaxis_title="PM2.5 (µg/m³)"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# ------------------------------------------------
# HEATMAP
# ------------------------------------------------

st.header("PM2.5 Heatmap")

heatmap_option = st.selectbox(
    "Heatmap Type",
    ["Monthly", "Yearly"],
    key="heatmap_type"
)

# ------------------------------------------------
# MONTHLY HEATMAP
# ------------------------------------------------

if heatmap_option == "Monthly":

    years = sorted(df["year"].unique())

    heat_year = st.selectbox(
        "Select Year",
        years,
        index=len(years)-1,
        key="monthly_heatmap_year"
    )

    heat_month = st.selectbox(
        "Select Month",
        list(month_labels.keys()),
        format_func=lambda x: month_labels[x],
        key="monthly_heatmap_month"
    )

    heat_df = df[
        (df["year"] == heat_year) &
        (df["month"] == heat_month)
    ]

    sensor_heat = (
        heat_df
        .groupby(
            ["location_name", "day", "hour"]
        )["pm25"]
        .mean()
        .reset_index()
    )

    monthly_heat = (
        sensor_heat
        .groupby(["day", "hour"])["pm25"]
        .mean()
        .reset_index()
    )

    pivot = monthly_heat.pivot(
        index="hour",
        columns="day",
        values="pm25"
    )

    pivot = pivot.reindex(
        columns=range(1, 32)
    )

    pivot = pivot.reindex(
        index=range(24)
    )

    pivot.index = [
        hour_labels[h]
        for h in pivot.index
    ]

    fig4 = px.imshow(
        pivot,
        aspect="auto",
        labels=dict(
            x="Day of Month",
            y="Time",
            color="PM2.5"
        )
    )

    fig4.update_layout(
        title=f"Monthly PM2.5 Heatmap — {month_labels[heat_month]} {heat_year}",
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# ------------------------------------------------
# YEARLY HEATMAP
# ------------------------------------------------

else:

    years = sorted(df["year"].unique())

    heat_year = st.selectbox(
        "Select Heatmap Year",
        years,
        index=len(years)-1,
        key="yearly_heatmap_year"
    )

    heat_df = df[
        df["year"] == heat_year
    ]

    sensor_heat = (
        heat_df
        .groupby(
            ["location_name", "month", "hour"]
        )["pm25"]
        .mean()
        .reset_index()
    )

    yearly_heat = (
        sensor_heat
        .groupby(["month", "hour"])["pm25"]
        .mean()
        .reset_index()
    )

    pivot = yearly_heat.pivot(
        index="hour",
        columns="month",
        values="pm25"
    )

    pivot = pivot.reindex(
        columns=range(1, 13)
    )

    pivot = pivot.reindex(
        index=range(24)
    )

    pivot.columns = [
        month_short[m]
        for m in pivot.columns
    ]

    pivot.index = [
        hour_labels[h]
        for h in pivot.index
    ]

    fig4 = px.imshow(
        pivot,
        aspect="auto",
        labels=dict(
            x="Month",
            y="Time",
            color="PM2.5"
        )
    )

    fig4.update_layout(
        title=f"Yearly PM2.5 Heatmap — {heat_year}"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# ------------------------------------------------
# INTERPOLATED HEATMAP
# ------------------------------------------------

st.header("Interpolated PM2.5 Heatmap")

pivot_interp = pivot.interpolate(
    axis=1,
    limit_direction="both"
)

fig5 = px.imshow(
    pivot_interp,
    aspect="auto",
    labels=dict(
        x="Time Axis",
        y="Hour",
        color="Interpolated PM2.5"
    )
)

fig5.update_layout(
    title="Interpolated PM2.5 Heatmap"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# ------------------------------------------------
# SUMMARY STATISTICS
# ------------------------------------------------

st.header("Summary Statistics")

st.dataframe(
    df["pm25"].describe()
)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from map_visualization import create_sensor_map

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(
    page_title="Kathmandu PM2.5 Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------
# CUSTOM STYLING
# ------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

h1 {
    color: #1f3b73;
    font-weight: 700;
}

h2, h3 {
    color: #244a8f;
}

[data-testid="metric-container"] {
    background-color: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    border-left: 5px solid #4f8bf9;
}

.stPlotlyChart {
    background-color: white;
    padding: 10px;
    border-radius: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# TITLE
# ------------------------------------------------

st.title("Kathmandu PM2.5 Dashboard")

st.markdown("""
This dashboard analyzes PM2.5 air pollution across Kathmandu using aggregated sensor measurements.

PM2.5 refers to airborne fine particulate matter smaller than 2.5 micrometers associated with respiratory and cardiovascular health risks.
""")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

df = pd.read_csv("clean_kathmandu_pm25.csv")
sensor_df = pd.read_csv("kathmandu_pm25_sensors.csv")

df.columns = df.columns.str.strip()
sensor_df.columns = sensor_df.columns.str.strip()

# ------------------------------------------------
# MERGE SENSOR DATA
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
# SIDEBAR FILTERS
# ------------------------------------------------

st.sidebar.header("Dashboard Filters")

available_years = sorted(df["year"].unique())

selected_years = st.sidebar.multiselect(
    "Select Year(s)",
    available_years,
    default=[max(available_years)]
)

available_sensors = sorted(
    df["location_name"]
    .dropna()
    .unique()
)

selected_sensors = st.sidebar.multiselect(
    "Select Sensors",
    available_sensors,
    default=available_sensors
)

# FILTER DATA

df = df[
    (df["year"].isin(selected_years)) &
    (df["location_name"].isin(selected_sensors))
]

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
    aq_color = "#2ecc71"

elif latest_pm25 <= 35:
    category = "Moderate"
    aq_color = "#f1c40f"

elif latest_pm25 <= 55:
    category = "Unhealthy for Sensitive Groups"
    aq_color = "#e67e22"

elif latest_pm25 <= 150:
    category = "Unhealthy"
    aq_color = "#e74c3c"

else:
    category = "Hazardous"
    aq_color = "#8e44ad"

# AQ CARD

st.markdown(
    f"""
    <div style="
        background-color:{aq_color};
        padding:18px;
        border-radius:14px;
        color:white;
        font-size:22px;
        font-weight:bold;
        text-align:center;
        margin-bottom:20px;
    ">
        Current AQ Category: {category}
    </div>
    """,
    unsafe_allow_html=True
)

a1, a2 = st.columns(2)

a1.metric(
    "Latest PM2.5",
    round(latest_pm25, 2)
)

a2.metric(
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

available_dates = sorted(df["date"].unique())

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
        line=dict(color="#1f77b4", width=3)
    )
)

fig.add_hline(
    y=15,
    line_dash="dash",
    line_color="red",
    annotation_text="WHO Guideline"
)

fig.update_layout(
    template="plotly_white",
    hovermode="x unified",
    title=f"Hourly PM2.5 Trend — {selected_date}",
    title_x=0.02,
    xaxis_title="Hour",
    yaxis_title="PM2.5 (µg/m³)",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# TABS
# ------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "Average Trends",
    "Heatmaps",
    "Interpolated Heatmap"
])

# =================================================
# TAB 1
# =================================================

with tab1:

    st.header("Average PM2.5 Trend")

    trend_option = st.selectbox(
        "Trend Type",
        ["Monthly", "Yearly"],
        key="trend_option"
    )

    # MONTHLY

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
                line=dict(color="#16a085", width=3)
            )
        )

        fig2.add_hline(
            y=15,
            line_dash="dash",
            line_color="red",
            annotation_text="WHO Guideline"
        )

        fig2.update_layout(
            template="plotly_white",
            hovermode="x unified",
            title=f"Daily Average PM2.5 — {month_labels[selected_month]} {selected_year}",
            title_x=0.02,
            xaxis_title="Day",
            yaxis_title="PM2.5 (µg/m³)",
            height=500,
            xaxis=dict(
                tickmode="linear",
                dtick=1
            )
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    # YEARLY

    else:

        years = sorted(df["year"].unique())

        selected_year = st.selectbox(
            "Select Year",
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
                line=dict(color="#8e44ad", width=3)
            )
        )

        fig3.add_hline(
            y=15,
            line_dash="dash",
            line_color="red",
            annotation_text="WHO Guideline"
        )

        fig3.update_layout(
            template="plotly_white",
            hovermode="x unified",
            title=f"Monthly Average PM2.5 — {selected_year}",
            title_x=0.02,
            xaxis_title="Month",
            yaxis_title="PM2.5 (µg/m³)",
            height=500
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

# =================================================
# TAB 2
# =================================================

with tab2:

    st.header("PM2.5 Heatmap")

    heatmap_option = st.selectbox(
        "Heatmap Type",
        ["Monthly", "Yearly"],
        key="heatmap_type"
    )

    # MONTHLY HEATMAP

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
            color_continuous_scale="RdYlGn_r",
            labels=dict(
                x="Day",
                y="Time",
                color="PM2.5"
            )
        )

        fig4.update_layout(
            template="plotly_white",
            title=f"Monthly PM2.5 Heatmap — {month_labels[heat_month]} {heat_year}",
            title_x=0.02,
            height=600,
            xaxis=dict(
                tickmode="linear",
                dtick=1
            )
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

    # YEARLY HEATMAP

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

        fig5 = px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale="RdYlGn_r",
            labels=dict(
                x="Month",
                y="Time",
                color="PM2.5"
            )
        )

        fig5.update_layout(
            template="plotly_white",
            title=f"Yearly PM2.5 Heatmap — {heat_year}",
            title_x=0.02,
            height=600
        )

        st.plotly_chart(
            fig5,
            use_container_width=True
        )
# =================================================
# TAB 3 - INTERPOLATED HEATMAP
# =================================================


with tab3:

    st.header("Interpolated PM2.5 Heatmap")

    interp_type = st.selectbox(
        "Interpolated Heatmap Type",
        ["Monthly", "Yearly"],
        key="interp_heatmap_type"
    )

    # ------------------------------------------------
    # MONTHLY INTERPOLATED
    # ------------------------------------------------

    if interp_type == "Monthly":

        years = sorted(df["year"].unique())

        interp_year = st.selectbox(
            "Select Year",
            years,
            index=len(years)-1,
            key="interp_month_year"
        )

        interp_month = st.selectbox(
            "Select Month",
            list(month_labels.keys()),
            format_func=lambda x: month_labels[x],
            key="interp_month"
        )

        interp_df = df[
            (df["year"] == interp_year) &
            (df["month"] == interp_month)
        ]

        sensor_interp = (
            interp_df
            .groupby(
                ["location_name", "day", "hour"]
            )["pm25"]
            .mean()
            .reset_index()
        )

        interp_heat = (
            sensor_interp
            .groupby(["day", "hour"])["pm25"]
            .mean()
            .reset_index()
        )

        pivot_interp = interp_heat.pivot(
            index="hour",
            columns="day",
            values="pm25"
        )

        # ALL DAYS
        pivot_interp = pivot_interp.reindex(
            columns=range(1, 32)
        )

        # ALL HOURS
        pivot_interp = pivot_interp.reindex(
            index=range(24)
        )

        # INTERPOLATION
        pivot_interp = pivot_interp.interpolate(
            axis=1,
            limit_direction="both"
        )

        # 12-HOUR LABELS
        pivot_interp.index = [
            hour_labels[h]
            for h in pivot_interp.index
        ]

        fig6 = px.imshow(
            pivot_interp,
            aspect="auto",
            color_continuous_scale="RdYlGn_r",
            labels=dict(
                x="Day",
                y="Time",
                color="PM2.5"
            )
        )

        fig6.update_layout(
            template="plotly_white",
            title=f"Interpolated Monthly Heatmap — {month_labels[interp_month]} {interp_year}",
            title_x=0.02,
            height=600,
            xaxis=dict(
                tickmode="linear",
                dtick=1
            )
        )

        st.plotly_chart(
            fig6,
            use_container_width=True
        )

    # ------------------------------------------------
    # YEARLY INTERPOLATED
    # ------------------------------------------------

    else:

        years = sorted(df["year"].unique())

        interp_year = st.selectbox(
            "Select Year",
            years,
            index=len(years)-1,
            key="interp_year"
        )

        interp_df = df[
            df["year"] == interp_year
        ]

        sensor_interp = (
            interp_df
            .groupby(
                ["location_name", "month", "hour"]
            )["pm25"]
            .mean()
            .reset_index()
        )

        interp_heat = (
            sensor_interp
            .groupby(["month", "hour"])["pm25"]
            .mean()
            .reset_index()
        )

        pivot_interp = interp_heat.pivot(
            index="hour",
            columns="month",
            values="pm25"
        )

        # ALL MONTHS
        pivot_interp = pivot_interp.reindex(
            columns=range(1, 13)
        )

        # ALL HOURS
        pivot_interp = pivot_interp.reindex(
            index=range(24)
        )

        # INTERPOLATION
        pivot_interp = pivot_interp.interpolate(
            axis=1,
            limit_direction="both"
        )

        # MONTH LABELS
        pivot_interp.columns = [
            month_short[m]
            for m in pivot_interp.columns
        ]

        # 12-HOUR LABELS
        pivot_interp.index = [
            hour_labels[h]
            for h in pivot_interp.index
        ]

        fig6 = px.imshow(
            pivot_interp,
            aspect="auto",
            color_continuous_scale="RdYlGn_r",
            labels=dict(
                x="Month",
                y="Time",
                color="PM2.5"
            )
        )

        fig6.update_layout(
            template="plotly_white",
            title=f"Interpolated Yearly Heatmap — {interp_year}",
            title_x=0.02,
            height=600
        )

        st.plotly_chart(
            fig6,
            use_container_width=True
        )

# =================================================
# SENSOR MAP
# =================================================

st.header("Kathmandu Sensor Map")
map_dates = sorted(
    df["date"].unique()
)

selected_map_date = st.selectbox(
    "Select Map Date",
    map_dates,
    index=len(map_dates)-1,
    key="map_date"
)
map_fig = create_sensor_map(
    df,
    selected_map_date
)

st.plotly_chart(
    map_fig,
    use_container_width=True
)


# ------------------------------------------------
# SUMMARY STATISTICS
# ------------------------------------------------

st.header("Summary Statistics")

st.dataframe(
    df["pm25"].describe(),
    use_container_width=True
)

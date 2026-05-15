import plotly.express as px
import pandas as pd


# =================================================
# AQ CATEGORY COLOR FUNCTION
# =================================================

def get_aq_color(pm25):

    if pm25 <= 15:
        return "Good"

    elif pm25 <= 35:
        return "Moderate"

    elif pm25 <= 55:
        return "USG"

    elif pm25 <= 150:
        return "Unhealthy"

    else:
        return "Hazardous"


# =================================================
# CREATE SENSOR MAP
# =================================================

def create_sensor_map(df, selected_date):

    # ---------------------------------------------
    # LATEST SENSOR VALUES
    # ---------------------------------------------

    latest_time = df["datetime"].max()

    map_df = df[
        df["date"] == selected_date
        ]

    sensor_map_df = (
        map_df
        .groupby(
            [
                "location_name",
                "latitude",
                "longitude"
            ]
        )["pm25"]
        .mean()
        .reset_index()
    )

    # ---------------------------------------------
    # AQ CATEGORY
    # ---------------------------------------------

    sensor_map_df["AQ Category"] = (
        sensor_map_df["pm25"]
        .apply(get_aq_color)
    )

    # ---------------------------------------------
    # MAP
    # ---------------------------------------------

    fig = px.scatter_mapbox(
        sensor_map_df,
        lat="latitude",
        lon="longitude",
        color="pm25",
        size="pm25",
        hover_name="location_name",
        hover_data={
            "pm25": True,
            "latitude": False,
            "longitude": False
        },
        color_continuous_scale="Turbo",
        size_max=28,
        zoom=11.8,
        height=650
    )

    # ---------------------------------------------
    # MAP STYLING
    # ---------------------------------------------

    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=50, b=0),
        title="Kathmandu PM2.5 Sensor Map",
        title_x=0.02,
        template="plotly_white"
    )

    return fig
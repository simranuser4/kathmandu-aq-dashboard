
import requests
import pandas as pd
import time

# -----------------------------------
# API KEY
# -----------------------------------

API_KEY = "c23fcdc1f2a7a42aba78b50870e0e184a13289c88b3d0b578fd57b07fd9654c6"

headers = {
    "X-API-Key": API_KEY
}

# -----------------------------------
# LOAD SENSOR CSV
# -----------------------------------

df_sensors = pd.read_csv(
    "kathmandu_pm25_sensors.csv"
)

print("\nTotal Sensors:")
print(len(df_sensors))

# -----------------------------------
# STORE DATA
# -----------------------------------

all_data = []

# -----------------------------------
# LOOP THROUGH SENSORS
# -----------------------------------

for sensor_id in df_sensors["sensor_id"]:

    print("\nChecking Sensor:", sensor_id)
    time.sleep(1)
    url = (
        f"https://api.openaq.org/v3/sensors/"
        f"{sensor_id}/measurements"
    )

    response = requests.get(
        url,
        headers=headers,
        params={"limit": 100},
        verify=False
    )

    print("Status:", response.status_code)


    id = "jlwm5z"
    # Skip failed API calls
    if response.status_code != 200:
        print("API Failed")
        continue

    # Convert to JSON
    data = response.json()


    # Skip bad sensors
    if "results" not in data:

        print("No results")
        continue

    results = data["results"]

    print("Rows Found:", len(results))

    # Skip empty results
    if len(results) == 0:
        continue

    # Extract data
    for row in results:

        try:

            all_data.append({

                "sensor_id": sensor_id,

                "datetime":
                    row["period"]
                    ["datetimeFrom"]
                    ["local"],

                "pm25":
                    row["value"]

            })

        except Exception as e:

            print("Error:", e)

# -----------------------------------
# CREATE DATAFRAME
# -----------------------------------

df = pd.DataFrame(all_data)

print("\nFINAL DATAFRAME")
print(df.head())

print("\nTotal Rows:")
print(len(df))

# -----------------------------------
# SAVE CSV
# -----------------------------------

df.to_csv(
    "kathmandu_pm25_all.csv",
    index=False
)

print("\nCSV SAVED")


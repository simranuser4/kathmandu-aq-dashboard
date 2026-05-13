# pip install pandas numpy

import pandas as pd
import numpy as np

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("kathmandu_pm25_all.csv")

print("\nRAW DATA")
print(df.head())

print("\nCOLUMNS")
print(df.columns.tolist())

print("\nSHAPE")
print(df.shape)

# -----------------------------
# FIND PM2.5 COLUMN
# -----------------------------
possible_cols = [
    "pm25",
    "value",
    "pm2.5",
    "pm_25"
]

pm_col = None

for col in possible_cols:
    if col in df.columns:
        pm_col = col
        break

# if still not found
if pm_col is None:

    for col in df.columns:

        if "pm" in col.lower():
            pm_col = col
            break

# rename to standard name
if pm_col is not None:

    df = df.rename(columns={
        pm_col: "pm25"
    })

    print("\nPM2.5 COLUMN FOUND:")
    print(pm_col)

else:

    print("\nNo PM2.5 column found.")
    exit()

# -----------------------------
# DATETIME
# -----------------------------
if "datetime" in df.columns:

    df["datetime"] = pd.to_datetime(df["datetime"])

# -----------------------------
# NULL VALUES
# -----------------------------
print("\nMISSING VALUES")
print(df.isnull().sum())

# -----------------------------
# REMOVE DUPLICATES
# -----------------------------
duplicates = df.duplicated().sum()

print("\nDUPLICATES:", duplicates)

df = df.drop_duplicates()

# -----------------------------
# REMOVE IMPOSSIBLE VALUES
# -----------------------------
print("\nREMOVING IMPOSSIBLE VALUES")

before = len(df)

df = df[df["pm25"] >= 0]
df = df[df["pm25"] <= 500]

after = len(df)

print("REMOVED:", before - after)

# -----------------------------
# OUTLIER DETECTION (IQR)
# -----------------------------
Q1 = df["pm25"].quantile(0.25)
Q3 = df["pm25"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print("\nOUTLIER RANGE")
print("LOWER:", lower)
print("UPPER:", upper)

# -----------------------------
# FIND OUTLIERS
# -----------------------------
outliers = df[
    (df["pm25"] < lower) |
    (df["pm25"] > upper)
]

print("\nTOTAL OUTLIERS:", len(outliers))

# -----------------------------
# SHOW TOP OUTLIERS
# -----------------------------
print("\nTOP OUTLIERS")

print(
    outliers.sort_values(
        by="pm25",
        ascending=False
    ).head(20)
)

# -----------------------------
# SAVE OUTLIERS
# -----------------------------
outliers.to_csv(
    "pm25_outliers.csv",
    index=False
)

print("\nOutliers saved")

# -----------------------------
# REMOVE OR KEEP
# -----------------------------
choice = input(
    "\nRemove outliers? (yes/no): "
).lower()

if choice == "yes":

    df_clean = df[
        (df["pm25"] >= lower) &
        (df["pm25"] <= upper)
    ]

    print("\nOUTLIERS REMOVED")

else:

    df_clean = df.copy()

    print("\nOUTLIERS KEPT")

# -----------------------------
# SAVE CLEAN DATA
# -----------------------------
df_clean.to_csv(
    "clean_kathmandu_pm25.csv",
    index=False
)

print("\nCLEAN DATA SHAPE")
print(df_clean.shape)

# -----------------------------
# SUMMARY
# -----------------------------
print("\nSUMMARY")

print(
    df_clean["pm25"].describe()
)

print("\nSaved:")
print("clean_kathmandu_pm25.csv")
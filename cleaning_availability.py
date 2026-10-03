import pandas as pd

raw_df = pd.read_csv("v1_remit_production_unavailability.csv")

# 1. Drop unwanted columns 
print(raw_df.columns.to_list())
raw_df = raw_df.drop(columns=['dataset','messageType','messageHeading','participantId','unavailableCapacity','cause', 'affectedUnitEIC', 'affectedArea','durationUncertainty', 'relatedInformation', 'outageProfile'])

# 2. Filter out eventStatus = Active and assetType = Production
raw_df = raw_df[
    (raw_df["eventStatus"]=="Active") & (raw_df["assetType"]=="Production")
]
raw_df=raw_df.drop_duplicates()

raw_df = raw_df[(
    raw_df["eventEndTime"]
    > raw_df["eventStartTime"]
)]
raw_df = raw_df.dropna(subset=['fuelType'])

raw_df = raw_df.loc[
    raw_df.groupby(
        ["assetId", "eventStartTime", "eventEndTime"]
    )["revisionNumber"].idxmax()
].reset_index(drop=True)

# 3. Ensure event columns are in datetime format
raw_df["eventStartTime"] = pd.to_datetime(raw_df["eventStartTime"])
raw_df["eventEndTime"] = pd.to_datetime(raw_df["eventEndTime"])


def generate_month_ranges(row):
    start = row["eventStartTime"]
    end = row["eventEndTime"]

    # Generate start of each month covering the range [start, end]
    # 'MS' stands for Month Start
    month_starts = pd.date_range(
        start=start.floor("D"), end=end.floor("D"), freq="MS"
    )

    # If eventStartTime is mid-month, include its month's start date
    first_month_start = start.floor("D").replace(day=1)
    if first_month_start not in month_starts:
        month_starts = month_starts.insert(0, first_month_start)

    intervals = []
    for m_start in month_starts:
        # Month start is either the eventStartTime or the 1st of that month
        s = max(start, m_start)

        # Month end is either the eventEndTime or the last second of that month
        m_end = m_start + pd.offsets.MonthEnd(1) + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
        e = min(end, m_end)

        if s < e:
            intervals.append((s, e))

    return intervals


# 5. Apply function to create a list of tuples (startTimeSeries, endTimeSeries)
raw_df["_intervals"] = raw_df.apply(generate_month_ranges, axis=1)

# 6. Explode the list into individual rows (retains all other columns)
df_expanded = raw_df.explode("_intervals").reset_index(drop=True)

# 7. Split tuples into two separate columns
df_expanded[["startTimeSeries", "endTimeSeries"]] = pd.DataFrame(
    df_expanded["_intervals"].tolist(), index=df_expanded.index
)

# 8. Clean up temporary column
df_expanded.drop(columns=["_intervals"], inplace=True)

valid_periods = (
    df_expanded["eventStartTime"] < df_expanded["eventEndTime"]
)

print(
    "\nEvents where eventEndTime < eventStartTime:",
    valid_periods.sum()
)

df_expanded.to_csv("v2_timeseries_check.csv")
print(df_expanded["startTimeSeries"].isna().sum())




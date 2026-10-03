import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

OUTPUT_CSV = "v1_remit_production_unavailability.csv"
# OUTPUT_PARQUET = "v1_remit_production_unavailability.parquet"


# ============================================================
# SESSION WITH RETRIES
# ============================================================

def create_session():

    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True
    )

    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=10,
        pool_maxsize=10
    )

    session = requests.Session()

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


# ============================================================
# STEP 1
# GET REMIT MESSAGE LIST
# ============================================================

def get_message_list(session, start_date, end_date):

    url = f"{BASE_URL}/remit/list/by-event/stream"

    params = {
        "from": f"{start_date}T00:00:00Z",
        "to": f"{end_date}T00:00:00Z",
        "messageType": "UnavailabilitiesOfElectricityFacilities",
        "eventType": ["Production Unavailability"],
        "latestRevisionOnly": "false"
    }

    print("=" * 70)
    print("GETTING REMIT MESSAGE LIST")
    print("=" * 70)

    print(f"From : {start_date}")
    print(f"To   : {end_date}")

    response = session.get(
        url,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    messages = response.json()

    print(f"\nMessages found: {len(messages)}")

    return messages


# ============================================================
# STEP 2
# GET DETAILS FOR EACH MESSAGE
# ============================================================

def get_message_details(session, messages):

    records = []

    total = len(messages)

    print("\n")
    print("=" * 70)
    print("GETTING REMIT MESSAGE DETAILS")
    print("=" * 70)

    for index, message in enumerate(messages, start=1):

        message_id = message["id"]

        url = f"{BASE_URL}/remit/{message_id}"

        try:

            response = session.get(
                url,
                timeout=60
            )

            response.raise_for_status()

            result = response.json()

            data = result.get("data", [])

            if data:

                # Normally one record per message
                records.extend(data)

            else:

                print(
                    f"\nWARNING: No data returned for ID {message_id}"
                )

        except requests.RequestException as e:

            print(
                f"\nERROR: ID {message_id} -> {e}"
            )

        # Progress
        if index % 25 == 0 or index == total:

            print(
                f"Progress: {index}/{total} "
                f"({index / total * 100:.1f}%) | "
                f"Records: {len(records)}"
            )

    return records


# ============================================================
# STEP 3
# CREATE DATAFRAME
# ============================================================

def create_dataframe(records):

    df = pd.DataFrame(records)

    if df.empty:

        print("\nNo data returned.")

        return df

    # Convert timestamps to UTC datetime
    datetime_columns = [
        "publishTime",
        "createdTime",
        "eventStartTime",
        "eventEndTime"
    ]

    for column in datetime_columns:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                utc=True,
                errors="coerce"
            )

    # Sort chronologically
    if "eventStartTime" in df.columns:

        df = df.sort_values(
            ["eventStartTime", "assetId"],
            na_position="last"
        ).reset_index(drop=True)

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    start_time = time.time()

    session = create_session()

    # --------------------------------------------------------
    # 1. Get message IDs
    # --------------------------------------------------------

    messages = get_message_list(
        session,
        START_DATE,
        END_DATE
    )

    if not messages:

        print("\nNo REMIT messages found.")

        return

    # --------------------------------------------------------
    # 2. Get complete messages
    # --------------------------------------------------------

    records = get_message_details(
        session,
        messages
    )

    # --------------------------------------------------------
    # 3. Create DataFrame
    # --------------------------------------------------------

    df = create_dataframe(records)

    # --------------------------------------------------------
    # 4. Display information
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL DATA")
    print("=" * 70)

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    print("\nColumns:")

    for column in df.columns:

        print(f"  - {column}")

    print("\nFirst 5 rows:")

    print(df.head())

    # --------------------------------------------------------
    # 5. Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    # df.to_parquet(
    #     OUTPUT_PARQUET,
    #     index=False
    # )

    # --------------------------------------------------------
    # 6. Summary
    # --------------------------------------------------------

    elapsed = time.time() - start_time

    print("\n")
    print("=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)

    print(f"CSV     : {OUTPUT_CSV}")
    # print(f"Parquet : {OUTPUT_PARQUET}")
    print(f"Rows    : {len(df)}")
    print(f"Time    : {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
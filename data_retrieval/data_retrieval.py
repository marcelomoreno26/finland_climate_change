import pandas as pd
from tqdm import tqdm
import datetime as dt
from fmiopendata.wfs import download_stored_query
import os


def get_pairs(st: dt.datetime) -> list[tuple[str, str]]:
    """
    Generate time intervals of 122 days (larger intervals crashed server) between a start time and the current time.

    Args:
        st (datetime): The start time for generating time pairs.

    Returns:
        list: A list of tuples where each tuple contains a pair of ISO 8601 formatted strings 
              representing the start and end times for 122-day intervals.
    """
    et = st + dt.timedelta(hours=122*24)
    time_pairs = []
    while et < dt.datetime.today():
        st_str = st.isoformat(timespec="seconds") + "Z"
        et_str = et.isoformat(timespec="seconds") + "Z"
        time_pairs.append((st_str, et_str))
        st += dt.timedelta(hours=122*24)
        et += dt.timedelta(hours=122*24)

    return time_pairs


def get_data_records(pair: tuple[str, str]) -> list[dict]:
    """
    Download weather observation data for a single time pair and store it in a list of dictionaries.

    Args:
        pair (tuple): A tuple containing the start and end times (in ISO 8601 format) 
                      for querying weather observations.

    Returns:
        list: A list of dictionaries containing the weather observations for the given time pair.
    """
    data_records = []
    obs = download_stored_query("fmi::observations::weather::daily::multipointcoverage",
                                args=["bbox=18,55,35,75",
                                      "starttime=" + pair[0],
                                      "endtime=" + pair[1],
                                      "timestep=1440"])

    for date, values_dict in obs.data.items():
        for loc, values in values_dict.items():
            for obs_key, obs_value in values.items():
                location_meta = obs.location_metadata[loc]
                data_records.append({
                    "date": date,
                    "fmisid": location_meta["fmisid"],
                    "location": loc,
                    "latitude": location_meta["latitude"],
                    "longitude": location_meta["longitude"],
                    "observation": obs_key,
                    "value": obs_value["value"],
                    "units": obs_value["units"]
                })

    return data_records


def append_or_create_csv(new_data: pd.DataFrame, filename: str) -> None:
    """
    Append data to an existing CSV or create a new CSV if it doesn't exist.

    Args:
        new_data (pd.DataFrame): A pandas DataFrame containing the new data to append.
        csv_filename (str): The name of the CSV file to append to or create.
    """
    if os.path.exists(filename):
        existing = pd.read_csv(filename)
        updated = pd.concat([existing, new_data]).drop_duplicates().reset_index(drop=True)
        updated.to_csv(filename, index=False)
    else:
        new_data.drop_duplicates().reset_index(drop=True).to_csv(filename, index=False)


def save_data(pair_data: list[dict]) -> None:
    """
    Save or append the processed weather observation data into CSV files.

    Args:
        pair_data (list): A list of dictionaries containing weather observation data.
    """
    df = pd.DataFrame(pair_data).dropna(subset=['value']).reset_index(drop=True)

    # Save or append observation units
    append_or_create_csv(df[["observation", "units"]].drop_duplicates(), "./data_retrieval/raw_data/daily_observation_units.csv")

    # Save or append station metadata
    append_or_create_csv(df[["fmisid", "location", "latitude", "longitude"]].drop_duplicates(), "./data_retrieval/raw_data/daily_stations.csv")

    # Save or append weather data
    append_or_create_csv(df[["fmisid", "date", "observation", "value"]].drop_duplicates(), "./data_retrieval/raw_data/daily_finland_weather_data.csv")


def main():
    """
    Main function to generate time intervals, download weather data, and save the data incrementally.

    Workflow:
        1. Generate time pairs starting from given starting date.
        2. Download the weather data for each time pair.
        3. Save the processed data incrementally after each time pair.
        4. Break the loop and stop if any error occurs during an iteration.
    """
    time_pairs = get_pairs(dt.datetime(1970, 1, 1, 0, 0))

    for pair in tqdm(time_pairs):
        try:
            pair_data = get_data_records(pair)
            save_data(pair_data)
            print(f"Saved data for period: {pair[0]} to {pair[1]}")
        except Exception as e:
            print(f"Failed to retrieve data for period: {pair[0]} to {pair[1]}. Error: {e}")
            break


if __name__ == "__main__":
    main()

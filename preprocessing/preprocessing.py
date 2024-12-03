import h3pandas
import duckdb
import pandas as pd
from tqdm import tqdm
import numpy as np
import geopandas as gpd



def get_hex_df():
    """
    Loads the hex grid data from a GeoJSON file and returns it as a GeoDataFrame.
    
    Returns
    -------
    GeoDataFrame
        The GeoDataFrame containing hex grid data with 'h3_polyfill' as the index.
    """

    hex_df = gpd.read_file("./data/geodata/finland_hex.geojson").set_index("h3_polyfill")
    hex_df['centroid'] = hex_df['geometry'].to_crs(epsg=4326).centroid

    return hex_df



def get_database():
    """
    Sets up an in-memory DuckDB database and populates it with weather-related data.
    Creates indices and applies data cleaning transformations as required.

    Returns
    -------
    duckdb.DuckDBPyConnection
        A DuckDB connection object to the in-memory database.
    """
    
    conn = duckdb.connect(database=':memory:')
    conn.execute("""
    CREATE TABLE fact_weather (
        fmisid INTEGER,
        date DATE,
        observation VARCHAR,
        value FLOAT
    );
    """)
    conn.execute("""
    COPY fact_weather FROM './data_retrieval/raw_data/daily_finland_weather_data.csv' (DELIMITER ',', HEADER, NULL 'NA');
    """)
    conn.execute("CREATE INDEX idx_date_observation ON fact_weather (date, observation);")

    conn.execute("""
                UPDATE fact_weather
    SET value = 0
    WHERE observation IN ('Snow depth', 'Precipitation amount')
    AND value = -1;
    """)

    conn.execute("""
    CREATE TABLE dim_stations (
        fmisid INTEGER,
        station VARCHAR,
        latitude FLOAT,
        longitude FLOAT
    );
    """)

    conn.execute("""
        CREATE TABLE dim_units (
            observation VARCHAR,
            units VARCHAR
        );
        """)

    conn.execute("""
        COPY dim_stations FROM './data_retrieval/raw_data/daily_stations.csv' (DELIMITER ',', HEADER, NULL 'NA');
        """)

    conn.execute("""
        COPY dim_units FROM './data_retrieval/raw_data/daily_observation_units.csv' (DELIMITER ',', HEADER, NULL 'NA');
        """)
    
    return conn
    


def get_data(conn):
    """
    Extracts aggregated weather data with station information from the database.

    Parameters
    ----------
    conn : duckdb.DuckDBPyConnection
        The DuckDB connection object.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing weather data aggregated by station, year, month, and observation type,
        along with latitude and longitude for each station.
    """

    return conn.execute(f"""              
    WITH wd AS (
        SELECT 
            fmisid,
            strftime('%Y', date) as year,
            strftime('%m', date) as month,
            observation,
            AVG(value) AS value
        FROM fact_weather
        GROUP BY fmisid, year, month, observation)

    SELECT 
        wd.fmisid,
        wd.year,
        wd.month,
        wd.observation,
        s.latitude,
        s.longitude,
        wd.value
    FROM
        wd
    JOIN dim_stations s on s.fmisid = wd.fmisid
    """).fetchdf()



def get_closest_station(centroids, lat, lon):
    """
    Finds the closest centroid to each station based on latitude and longitude.

    Parameters
    ----------
    centroids : pandas.Series
        A Series containing shapely Point objects representing the centroids of hexagons.
    lat : pandas.Series
        A Series of latitude values for stations.
    lon : pandas.Series
        A Series of longitude values for stations.

    Returns
    -------
    numpy.ndarray
        An array of indices indicating the closest centroid for each station.
    """

    centroids_arr = np.array([(c.x, c.y) for c in centroids])
    points = np.array([(lon[i], lat[i]) for i in range(len(lat))])
    centroids_squared = np.sum(centroids_arr**2, axis=1)[:, np.newaxis]  # Shape (n_centroids, 1)
    points_squared = np.sum(points**2, axis=1)  # Shape (n_points,)
    squared_dist = centroids_squared + points_squared - 2 * np.dot(centroids_arr, points.T)
    
    return np.argmin(squared_dist, axis=1)



def get_observation_values(centroid, lat, lon, val):
    """
    Maps weather observation values to the closest hexagon centroids.

    Parameters
    ----------
    centroid : pandas.Series
        A Series of shapely Point objects representing hexagon centroids.
    lat : pandas.Series
        A Series of latitude values for weather stations.
    lon : pandas.Series
        A Series of longitude values for weather stations.
    val : pandas.Series
        A Series of weather observation values.

    Returns
    -------
    numpy.ndarray
        An array of weather observation values mapped to the closest hexagon centroids.
    """

    closest_idxs = get_closest_station(centroid, lat, lon)
    obs_values = np.array(val[closest_idxs].reset_index(drop=True))
    
    return obs_values



def main():
    """
    Main function to process weather data and map it to a hexagonal grid and regional averages.
    
    Steps:
    1. Extracts hexagonal grid data and initializes a DuckDB database with weather data.
    2. Groups the weather data by date and observation type.
    3. Maps weather observations to the closest hexagonal grid cells.
    4. Saves the hexagonal grid data with weather observations to a CSV file.
    5. Aggregates weather data by region and saves the regional averages to a separate CSV file.
    
    Outputs
    -------
    - Hexagonal grid weather data: './data/monthly_weather_data_hex.csv'
    - Regional weather averages: './data/monthly_weather_data_region.csv'
    """

    hex_df = get_hex_df()
    conn = get_database()
    data = get_data(conn)
    data['date'] = data['year'] + '-' + data['month']
    data_list = []
    grouped = data.groupby(['date','observation'])
    for date_obs_tuple, group in tqdm(grouped):
        group = group.reset_index(drop=True)
        values = get_observation_values(hex_df["centroid"], group["latitude"], group["longitude"], group["value"])
        data_list.append(pd.DataFrame({
            'hex_id': hex_df.index,  
            'date': date_obs_tuple[0],  
            'observation': date_obs_tuple[1],
            'value': values
        }))

    hex_climate_df = pd.concat(data_list)
    hex_climate_df = hex_climate_df.rename(columns={"hex_id":"index"}).round(1)
    hex_climate_df.to_csv("./monthly_weather_data_hex.csv", index=False)

    region_df = hex_climate_df.merge(hex_df.reset_index()[["h3_polyfill","region"]], left_on="index",right_on="h3_polyfill",how="inner").drop("h3_polyfill",axis=1)
    region_df = region_df.groupby(["observation","date","region"]).agg(value=("value","mean")).reset_index().round(1)
    region_df.rename(columns={"region":"index"})[["index","date","observation","value"]].to_csv("./monthly_weather_data_region.csv",index=False)

if __name__ == "__main__":
    main()
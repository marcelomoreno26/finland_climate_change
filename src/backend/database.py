import geopandas as gpd
import h3pandas
import duckdb



class Database():
    """
    Handles the loading of weather data, geospatial data for hex and region mapping, 
    and manages the DuckDB database connection.
    """
    def __init__(self):
        self.hex_df = self.GetHexDf()
        self.region_df = self.GetRegionDF()
        self.conn = self.LoadDuckDb()



    def GetHexDf(self):
        """
        Loads the hex grid data from a GeoJSON file and returns it as a GeoDataFrame.
        
        Returns
        -------
        GeoDataFrame
            The GeoDataFrame containing hex grid data with 'h3_polyfill' as the index.
        """
        hex_df = gpd.read_file("./data/geodata/finland_hex.geojson").set_index("h3_polyfill")
    
        return hex_df


    def GetRegionDF(self):
        """
        Loads the region data from a GeoJSON file, drops the 'source' column, 
        and returns it as a GeoDataFrame with 'id' as the index.
        
        Returns
        -------
        GeoDataFrame
            The GeoDataFrame containing region data.
        """
        return gpd.read_file("./data/geodata/finland_regions.json").drop("source",axis=1).set_index("id")
    

    def LoadDuckDb(self):
        """
        Loads the weather data into DuckDB, creating tables for hex and region-based data 
        and returns the DuckDB connection.
        
        Returns
        -------
        duckdb.DuckDBPyConnection
            The DuckDB connection object used to query the data.
        """

        conn = duckdb.connect(database=':memory:')

        conn.execute("""
        CREATE TABLE fact_weather_hex (
            index VARCHAR,
            date VARCHAR,
            observation VARCHAR,
            value FLOAT
        );
        """)

        conn.execute("""
        COPY fact_weather_hex FROM 'data/monthly_weather_data_hex.csv' (DELIMITER ',', HEADER, NULL 'NA');
        """)

        conn.execute("""
        CREATE INDEX idx_hex_date_observation ON fact_weather_hex (date, observation);
        """)

        conn.execute("""
        CREATE TABLE fact_weather_region (
            index VARCHAR,
            date VARCHAR,
            observation VARCHAR,
            value FLOAT
        );
        """)

        conn.execute("""
        COPY fact_weather_region FROM 'data/monthly_weather_data_region.csv' (DELIMITER ',', HEADER, NULL 'NA');
        """)

        conn.execute("""
        CREATE INDEX idx_region_date_observation ON fact_weather_region (date, observation);
        """)

        return conn
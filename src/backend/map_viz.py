from . import px, Viz
from abc import ABC



class MapViz(Viz, ABC):
    """
    Base class for map visualizations. Handles color map selection, tooltip creation, and 
    generation of choropleth maps for weather observations. It extends `Viz` and implements 
    methods for adding tooltips and setting color maps for visualizations.
    """
    def __init__(self, observation):
        super().__init__(observation)
        self.comparison = False
        self.cmap = self.SetCMap()

    
    def SetCMap(self):
        """
        Selects the appropriate color map based on the observation type and whether a comparison map is requested.

        Returns
        -------
        str
            The selected color map name (e.g., "RdBu_r", "Blues", "Greys_r").
        """

        if not self.comparison:
            if self.observation == "Snow depth":
                return "Greys_r"        
            elif self.observation == "Air temperature":
                return "RdBu_r"        
            elif self.observation == "Precipitation amount":
                return "Blues"
        else:
            if self.observation == "Snow depth":
                return "RdBu"        
            elif self.observation == "Air temperature":
                return "RdBu_r"        
            elif self.observation == "Precipitation amount":
                return "rdylgn"


    def AddTooltip(self, db, df, data_level):
        """
        Adds tooltips to the DataFrame for visualizations based on the data level (hex or region).

        Parameters
        ----------
        db : Database
            The database object used to access region or hex data for tooltips.
        df : DataFrame
            The DataFrame containing the weather data to be visualized.
        data_level : str
            The level of the data ('hex' for hex grids or 'region' for regions).

        Returns
        -------
        DataFrame
            The input DataFrame with an additional "tooltip" column containing HTML-formatted tooltips.
        """
        if data_level == "hex":
            df["tooltip"] = df.apply(
                lambda row: f"<BR><b>{'∆' if self.comparison else ''}{self.observation}:</b> {row['value']:.2f} {self.units}<BR>"
                            f"<b>Date:</b> {row['date']}",
                axis=1
            ).tolist()
        elif data_level == "region":
            df = df.merge(db.region_df.reset_index()[['id', 'name']], left_on='index', right_on='id', how='left')
            df["tooltip"] = df.apply(
                lambda row: f"<BR><b>{'∆' if self.comparison else ''}{self.observation}:</b> {row['value']:.2f} {self.units}<BR>"
                            f"<b>Date:</b> {row['date']}<BR>"
                            f"<b>Region:</b> {row['name']}",
                axis=1
            ).tolist()

        return df
 
    
    def GetViz(self, db, config):
        """
        Generates a choropleth map visualization using Plotly for the given weather data, 
        including color scales, tooltips, and map settings.

        Parameters
        ----------
        db : Database
            The database object used to retrieve the geospatial data (hex or region).
        config : dict
            A dictionary containing configuration parameters for the query, including data level ('hex' or 'region').

        Returns
        -------
        plotly.graph_objs.Figure
            The generated Plotly choropleth map figure.
        """
        df = self.Query(db, **config)    

        if self.comparison or self.observation == "Air temperature":
            max_abs_value = max(abs(df.value.min()), abs(df.value.max()))
            vmin, vmax = -max_abs_value, max_abs_value
        else:
            vmin, vmax = 0, df.value.max()
            df["value"] = list(map(lambda x: x if x > 0 else None, df["value"]))

        df = self.AddTooltip(db, df, config["data_level"])

        fig = px.choropleth_mapbox(
            df, 
            geojson=db.hex_df.geometry.__geo_interface__ if config["data_level"] =="hex" else db.region_df.geometry.__geo_interface__,  
            locations='index', 
            color='value', 
            color_continuous_scale=self.cmap,  
            range_color=(vmin, vmax),
            animation_frame='date',
            custom_data=["tooltip"],
            zoom=4,
            width=300,
            height=800,
            center={"lat": 65.5, "lon": 26.0},
            labels={'val': self.observation},
            mapbox_style="carto-positron",
            opacity=0.75
        )

        fig.update_coloraxes(colorbar_title=f"Avg. {'∆' if self.comparison else ''}{self.observation} in {self.units}")

        CUSTOM_HOVERTEMPLATE = "%{customdata[0]}<extra></extra>"
        fig.update_traces(hovertemplate=CUSTOM_HOVERTEMPLATE)
        for frame in fig.frames:
            frame.data[0].hovertemplate = CUSTOM_HOVERTEMPLATE
        
        fig.update_geos(projection_type="equirectangular", visible=True, resolution=110)

        
        return fig



class YearRoundMonthlyMapViz(MapViz):
    def Query(self, db, data_level,start_year,rolling_window=1):
        """
        Queries year-round monthly weather data for a specific observation, applying a rolling window for 
        monthly values. The data includes all months from January to December over a five-year period, 
        with results displayed by either hex grid or region based on `data_level`.
        """

        query = f"""
        WITH processed_data AS (
            SELECT 
            index,
            date, 
            AVG(value) OVER (
                PARTITION BY index, SUBSTR(date, 6, 2)
                ORDER BY date
                ROWS BETWEEN {rolling_window - 1} PRECEDING AND CURRENT ROW
            ) AS value
        FROM fact_weather_{data_level}
        WHERE observation = '{self.observation}'
        ORDER BY index, date
        )

        SELECT 
            *
        FROM processed_data
        WHERE SUBSTR(date, 1, 4) BETWEEN {start_year} AND {start_year + 5};
        """

        return db.conn.execute(query).fetchdf()
    


class YearlyMapViz(MapViz):
    def Query(self, db, data_level, start_year, end_year, rolling_window=1):
        """
        Queries yearly weather data for a specific observation, applying a rolling window to smooth the values, 
        and returns aggregated yearly data (averaged over time) for each specific region or hex grid. 
        The data is returned for the specified range of years (`start_year` to `end_year`), 
        with results displayed by either hex grid or region based on `data_level`.
        """

        query = f"""
        WITH aggregated_data AS (
            SELECT
                index,
                CAST(LEFT(date, 4) AS INT) AS year,  -- Extract the year from YYYY-MM
                AVG(value) AS avg_value
            FROM fact_weather_{data_level}
            WHERE observation = '{self.observation}'
            GROUP BY index, year
        ),
        rolling_data AS (
            SELECT
                index,
                year,
                AVG(avg_value) OVER (
                    PARTITION BY index
                    ORDER BY year
                    ROWS BETWEEN {rolling_window - 1} PRECEDING AND CURRENT ROW
                ) AS value
            FROM aggregated_data
        )
        SELECT 
            index,
            year AS date,
            value
        FROM rolling_data
        WHERE year BETWEEN {start_year} AND {end_year}
        ORDER BY index, year;
        """

        return db.conn.execute(query).fetchdf()

    

class SingleMonthMapViz(MapViz):
    def Query(self, db, data_level, start_year, end_year, month, rolling_window):
        """
        Queries weather data for a specific observation and month, applying a rolling window to smooth the values. 
        The data is returned for the specified month across a range of years (`start_year` to `end_year`), 
        with results displayed by either hex grid or region based on `data_level`.
        """

        query = f"""
        WITH filtered_data AS (
            SELECT 
                index,
                date,
                value
            FROM 
                fact_weather_{data_level}
            WHERE 
                observation = '{self.observation}'
                AND SUBSTR(date, 6, 2) = '{month:02d}'  -- Filter for the specified month
        ),
        rolling_data AS (
            SELECT 
                index,
                date,
                AVG(value) OVER (
                    PARTITION BY index
                    ORDER BY date
                    ROWS BETWEEN {rolling_window - 1} PRECEDING AND CURRENT ROW
                ) AS value
            FROM filtered_data
        )
        SELECT 
            index,
            date,
            value
        FROM rolling_data
        WHERE CAST(SUBSTR(date, 1, 4) AS INT) BETWEEN {start_year} AND {end_year}
        ORDER BY index, date;
        """

        return db.conn.execute(query).fetchdf()
        


class YearlyComparisonMapViz(MapViz):
    def __init__(self, observation):
        super().__init__(observation)
        self.comparison = True
        self.cmap = self.SetCMap()  

    
    def Query(self, db, data_level, comparison_year, start_year, end_year, rolling_window=1):
        """
        Queries yearly weather data for a specific observation, applying a rolling window to smooth the values, 
        and compares the data against a specified `comparison_year`. 
        The result shows the difference between the values for the given years (`start_year` to `end_year`) 
        and the comparison year, with data displayed by either hex grid or region based on `data_level`.
        """

        query = f"""
        WITH aggregated_data AS (
            SELECT
                index,
                CAST(LEFT(date, 4) AS INT) AS year,  -- Extract the year from YYYY-MM
                AVG(value) AS value
            FROM fact_weather_{data_level}
            WHERE observation = '{self.observation}'
            GROUP BY index, year
        ),
        rolling_data AS (
            SELECT 
                index,
                year AS date,
                AVG(value) OVER (
                    PARTITION BY index
                    ORDER BY year
                    ROWS BETWEEN {rolling_window - 1} PRECEDING AND CURRENT ROW
                ) AS value
            FROM aggregated_data
        ),
        comparison_data AS (
            SELECT 
                index,
                value AS comparison_value
            FROM rolling_data
            WHERE date = {comparison_year}
        )
        SELECT 
            r.index,
            r.date,
            r.value - c.comparison_value AS value
        FROM rolling_data r
        LEFT JOIN comparison_data c
            ON r.index = c.index
        WHERE r.date BETWEEN {start_year} AND {end_year}
        ORDER BY r.index, r.date;
        """

        return db.conn.execute(query).fetchdf()



class SingleMonthComparisonMapViz(MapViz):
    def __init__(self, observation):
        super().__init__(observation)
        self.comparison = True
        self.cmap = self.SetCMap()        


    def Query(self, db, data_level, start_year, end_year, month, rolling_window, comparison_year):
        """
        Queries weather data for a specific observation and month, applying a rolling window to smooth the values, 
        and compares the results with data from a specified `comparison_period` (which includes both year and month). 
        The query returns the difference between the values for the given month across a range of years (`start_year` to `end_year`), 
        with data displayed by either hex grid or region based on `data_level`.
        """

        query = f"""
        WITH filtered_data AS (
            SELECT 
                index,
                date,
                value
            FROM 
                fact_weather_{data_level}
            WHERE 
                observation = '{self.observation}'
                AND SUBSTR(date, 6, 2) = '{month:02d}'  -- Filter for the same month
        ),
        rolling_data AS (
            SELECT 
                index,
                date,
                AVG(value) OVER (
                    PARTITION BY index
                    ORDER BY date
                    ROWS BETWEEN {rolling_window - 1} PRECEDING AND CURRENT ROW
                ) AS value
            FROM filtered_data
        ),
        comparison_data AS (
            SELECT 
                index,
                value AS comparison_value
            FROM rolling_data
            WHERE CAST(SUBSTR(date, 1, 4) AS INT) = {comparison_year}
        )
        SELECT 
            r.index,
            r.date,
            r.value - c.comparison_value AS value
        FROM rolling_data r
        LEFT JOIN comparison_data c
            ON r.index = c.index
        WHERE CAST(SUBSTR(r.date, 1, 4) AS INT) BETWEEN {start_year} AND {end_year}
        ORDER BY r.index, r.date;
        """

        return db.conn.execute(query).fetchdf()
    
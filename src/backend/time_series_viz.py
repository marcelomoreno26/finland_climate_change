from . import px, Viz
from abc import ABC



class TimeSeriesViz(Viz, ABC):
    """
    Class for creating time series visualizations of weather data, with support for displaying trend lines
    and tooltips with information for each region over time.
    """

    def AddTooltip(self, df):
        """
        Adds tooltips to the dataframe for hover information in the time series plot.

        Parameters
        ----------
        df : pandas.DataFrame
            Dataframe containing the data to be visualized.

        Returns
        -------
        pandas.DataFrame
            The dataframe with an added 'tooltip' column.
        """
        df["tooltip"] = df.apply(
            lambda row: f"<BR><b>{self.observation}:</b> {row['value']:.2f} {self.units}<BR>"
                        f"<b>Region:</b> {row['name']}",
            axis=1
        ).tolist()

        return df
    

    def GetViz(self, db, config):
        """
        Generates a time series plot of the data, with optional trend line.

        Parameters
        ----------
        db : Database
            Database object containing the necessary data.
        config : dict
            Configuration dictionary containing parameters such as 'trend_line'.

        Returns
        -------
        plotly.graph_objs.Figure
            The generated time series visualization.
        """
        df = self.Query(db,**{k:v for k,v in config.items() if k != "trend_line"})
        df = self.AddTooltip(df)
        
        
        fig = px.line(df, x='date', y='value', color='name',
            labels={'value': f'Avg. {self.observation} in {self.units}', 'date': 'Date'},
            custom_data=["tooltip"],
            markers=True)
        
        fig.update_traces(hovertemplate="%{customdata[0]}<extra></extra>")
        fig.update_layout(hovermode="x unified")
        fig.update_legends(title=f"Regions")

        
        if config["trend_line"]:    
            trend_traces = px.scatter(df, 
                    x='date', y='value', color='name',
                    trendline='ols').data[1:]
            
            for trace in trend_traces:
                trace.showlegend = False  
                trace.hoverinfo = "skip"
                trace.hovertemplate= None
                fig.add_trace(trace)

        
        return fig
    


class YearRoundMonthlyTimeSeriesViz(TimeSeriesViz):
    def Query(self, db, start_year, end_year, region_list,rolling_window):
        """
        This method generates a query that retrieves weather data for a specified set of regions, 
        with an option to apply a rolling window to average the data on a monthly basis. The query 
        returns data for each month of the year within the given start and end year range, considering 
        only the relevant observation and region data.
        """
        region_ids = tuple(db.region_df.reset_index().query(f"name in {region_list}")["id"])

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
        FROM fact_weather_region
        WHERE 1=1
        AND observation = '{self.observation}'
        AND index IN {region_ids}
        ORDER BY index, date
        )

        SELECT 
            *
        FROM processed_data
        WHERE SUBSTR(date, 1, 4) BETWEEN {start_year} AND {end_year};
        """

        df = db.conn.execute(query).fetchdf()
        df = df.merge(db.region_df.reset_index()[['id', 'name']], left_on='index', right_on='id', how='left').drop("id",axis=1) # name retrieved for use in tooltip
        return df
    


class SingleMonthTimeSeriesViz(TimeSeriesViz):
    def Query(self, db, start_year, end_year, month, region_list,rolling_window):
        """
        Retrieves weather data for a specific month (e.g., January, February) across a set of regions, 
        applying a rolling window to average the data. The data is filtered by the specified month and year range.
        """

        region_ids = tuple(db.region_df.reset_index().query(f"name in {region_list}")["id"])
        
        query = f"""
        WITH filtered_data AS (
            SELECT 
                index,
                date,
                value
            FROM 
                fact_weather_region
            WHERE 1=1
            AND observation = '{self.observation}'
            AND index in {region_ids}
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

        df = db.conn.execute(query).fetchdf()
        df = df.merge(db.region_df.reset_index()[['id', 'name']], left_on='index', right_on='id', how='left').drop("id",axis=1) # name retrieved for use in tooltip
        
        return df



class YearlyTimeSeriesViz(TimeSeriesViz):
    def Query(self, db, start_year, end_year, region_list, rolling_window=1):
        """
        Retrieves weather data aggregated by year for a specified set of regions, applying a rolling window 
        to smooth the data. The data is limited to the specified year range and filtered by the provided 
        observation and regions.
        """

        region_ids = tuple(db.region_df.reset_index().query(f"name in {region_list}")["id"])

        query = f"""
        WITH aggregated_data AS (
            SELECT
                index,
                CAST(LEFT(date, 4) AS INT) AS year,  -- Extract the year from YYYY-MM
                AVG(value) AS avg_value
            FROM fact_weather_region
            WHERE 1=1
            AND observation = '{self.observation}'
            AND index in {region_ids}
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

        df = db.conn.execute(query).fetchdf()
        df = df.merge(db.region_df.reset_index()[['id', 'name']], left_on='index', right_on='id', how='left').drop("id",axis=1) # name retrieved for use in tooltip
        
        return df
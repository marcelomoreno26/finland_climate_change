from . import st, Page
from .utils import *
from backend import YearlyTimeSeriesViz, YearRoundMonthlyTimeSeriesViz, SingleMonthTimeSeriesViz



class TimeSeriesPage(Page):
    def __init__(self, db):
        super().__init__(db=db,
                         title="Time Series for Climate Data in Finland, 1960-2023",
                        description= "Time Series" )
        
    
    def InfoExpander(self):
        with st.expander("Visualization Types Descriptions"):
        
            with st.container():
                st.write("**NOTE:** A rolling window can be applied as specified in **Important features** to reduce noise and better observe trends.")
            
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("1. Yearly Climate Data")
                st.write("""
                    This visualization allows you to explore yearly climate data trends for specific regions over a custom time period. 
                    You can view the average yearly data (e.g., temperature, precipitation) for selected regions, and apply a rolling window 
                    to smooth the data and highlight long-term trends.  This enables a clearer view of gradual climate 
                    changes over time. Select the time range, regions, and observation type to explore the data.
                """)

            with col2:
                st.subheader("2. Single-Month Over Time Climate")
                st.write("""
                    This visualization allows you to focus on one specific month (e.g., January or July) and examine how its climate data changes across the years. 
                    It offers a detailed view of long-term trends within that single month, and you can compare the data over a custom time period. 
                    For example, explore how July rainfall patterns in Finland have shifted between 1970 and 2020.
                """)

            with col3:
                st.subheader("3. Year-Round Monthly Climate")
                st.write("""
                    This visualization displays how monthly climate data (e.g., temperature, snow depth, or precipitation) evolves over time, 
                    with data presented year-round. You can select a specific period (1960-2023) and explore how climate patterns change month by month. 
                    For example, you can track how temperatures or snowfall have changed throughout the year in Finland from 1990 to 2020.
                """)


        with st.expander("Important Features"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.subheader("1. Rolling Averages")
                st.write("""
                    Rolling averages (1, 5, or 10 years) can be applied to smooth out short-term fluctuations and reveal broader trends in the climate data. 
                    A shorter window (1-year) shows precise yearly data, while longer windows (5 or 10 years) smooth out more noise and allow for better long-term 
                    trend detection, such as shifts in temperature or precipitation.
                """)

            with col2:
                st.subheader("2. Region Selection")
                st.write("""
                    You can select one or more regions (Finland’s 19 administrative regions) to focus your analysis on. Choose regions like **Lapland** or **Uusimaa** 
                    to view the data specific to those areas. This feature enables a more granular look at how climate patterns differ across Finland.
                """)

            with col3:
                st.subheader("3. Trend Line")
                st.write("""
                    The trend line feature allows you to see overall trends in the climate data over time. When enabled, the trend line shows a smoothed view of the data, 
                    helping to identify patterns such as warming or cooling trends, or changes in precipitation.
                """)

            with col4:
                st.subheader("4. Interactive Plot")
                st.write("""
                    The visualizations are fully interactive. You can zoom in and out to focus on specific time periods. Additionally, by hovering over specific points on 
                    the graph, you can use the **tooltip** to view detailed values for specific months or years.
                """)
        
    
    def GetYearRoundMonthlyVizConfig(self):
        with st.container():
            self.observation = st.selectbox("Observation",self.observations)

        with st.container():
            period = st.selectbox("Rolling Average Window",self.periods)
            rolling_window = GetRollingWindow(period)
            min_year = GetMinYear(self.year_range[0],rolling_window)

        with st.container():
            region_list = st.multiselect("Regions", list(self.db.region_df.name), default=["Lapland","Uusimaa"])

        with st.container():
            start_year = st.slider("Start Year", min_value=min_year, max_value=self.year_range[1], value=min_year)
        
        with st.container():
            end_year = st.slider("End Year", min_value=min_year, max_value=self.year_range[1], value=self.year_range[1])

        with st.container():
            trend_line = st.checkbox("Trend Line")

        
        return {"region_list":region_list, "start_year":start_year, "end_year":end_year, "rolling_window":rolling_window, "trend_line":trend_line}
    

    def GetYearlyVizConfig(self):
        with st.container():
            self.observation = st.selectbox("Observation",self.observations)

        with st.container():
            period = st.selectbox("Rolling Average Window",self.periods)
            rolling_window = GetRollingWindow(period)
            min_year = GetMinYear(self.year_range[0],rolling_window)

        with st.container():
            region_list = st.multiselect("Regions", list(self.db.region_df.name), default=["Lapland","Uusimaa"])

        with st.container():
            start_year = st.slider("Start Year",min_value=min_year, max_value=self.year_range[1], value=min_year)

        with st.container():  
            end_year = st.slider("End Year", min_value=min_year, max_value=self.year_range[1], value=self.year_range[1])

        with st.container():
            trend_line = st.checkbox("Trend Line")
        
        return {"region_list": region_list, "start_year": start_year, "end_year": end_year,"rolling_window": rolling_window, "trend_line":trend_line}

    
    def GetSingleMonthVizConfig(self):
        with st.container():
            self.observation = st.selectbox("Observation",self.observations)

        with st.container():
            period = st.selectbox("Rolling Average Window",self.periods)
            rolling_window = GetRollingWindow(period)
            min_year = GetMinYear(self.year_range[0],rolling_window)

        with st.container():
            region_list = st.multiselect("Regions", list(self.db.region_df.name), default=["Lapland","Uusimaa"])
        
        with st.container():
            month = st.selectbox("Month", months)

        with st.container():
            start_year = st.slider("Start Year", min_value=min_year, max_value=self.year_range[1], value=min_year)
        
        with st.container():
            end_year = st.slider("End Year", min_value=min_year, max_value=self.year_range[1], value=self.year_range[1])

        with st.container():
            trend_line = st.checkbox("Trend Line")

        
        return  {"region_list":region_list, "start_year":start_year, "end_year":end_year, "month":GetMonth(month), "rolling_window":rolling_window, "trend_line":trend_line}
    


    def Run(self):
        _, left, right, _ = st.columns((1,2,4,1))

        with left:
            viz_type = st.selectbox("Time Series Type", ["Yearly Climate", "Year-Round Monthly Climate", "Single-Month Yearly Climate"], placeholder="Yearly Climate")

            if viz_type == "Year-Round Monthly Climate":
                config = self.GetYearRoundMonthlyVizConfig()
            elif viz_type == "Yearly Climate":
                config = self.GetYearlyVizConfig()
            elif viz_type == "Single-Month Yearly Climate":
                config = self.GetSingleMonthVizConfig()

        with right:
            for _ in range(3):
                with st.container():
                    st.empty()
            if viz_type == "Year-Round Monthly Climate":
                fig = YearRoundMonthlyTimeSeriesViz(self.observation).GetViz(self.db, config)
            elif viz_type == "Yearly Climate":
                fig = YearlyTimeSeriesViz(self.observation).GetViz(self.db, config)
            elif viz_type == "Single-Month Yearly Climate":
                fig = SingleMonthTimeSeriesViz(self.observation).GetViz(self.db, config)
            st.plotly_chart(fig, use_container_width=True)
from . import st, Page
from .utils import *
from backend import  YearRoundMonthlyMapViz, YearlyMapViz,SingleMonthMapViz, YearlyComparisonMapViz, SingleMonthComparisonMapViz



class MapPage(Page):
    def __init__(self, db):
        super().__init__(db=db,
                         title="Animated Maps for Climate Data in Finland, 1960-2023",
                         description= "Maps" )
        

    def InfoExpander(self):
        with st.expander("Visualization Types Descriptions"):
            
            with st.container():
                st.write("**NOTE:** A rolling window can be applied as specified in **Important features** to reduce noise and better observe trends.")
            
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("1. Year-Round Monthly Climate (Limited to 5 Years)")
                st.write("""
                    This animated map provides a year-round view of how monthly climate patterns 
                    (e.g., temperature, snow depth, or precipitation) have changed over a 5-year period. 
                    Each animation cycles through all 12 months for the selected years, offering insights 
                    into seasonal trends and how they evolve within the timeframe. Select a starting year and 
                    press play to observe changes month by month. For instance, explore how January snow depths 
                    and July rainfall varied across Finland during the period 1980–1984 compared to 2015–2019.
                """)

            with col2:
                st.subheader("2. Climate Data Over Time")
                st.write("""
                    This map type explores how climate patterns have changed over the years across Finland, allowing you to examine 
                    either a specific month (e.g., January or July) over time or simplt the yearly averages. You can select a broad time range 
                    spanning several decades to uncover long-term trends. By pressing play, you can observe how various climate 
                    indicators, such as winter temperatures or summer precipitation, have evolved over time. For instance, 
                    you could track how average January snow depths have changed between 1960 and 2020, or you can view the 
                    yearly average for a broader climate measure across the entire year, offering insights into overall trends.
                """)

            with col3:
                st.subheader("3. Comparison to a Baseline")
                st.write("""
                    This visualization compares data to a baseline across multiple years. As in *Climate Data Over Time* you can
                    select to see a specific month over time or yearly avergae. If you are visualizing a specific month then the baseline
                    is a specific year and the month being shown, otherwise the baseline is just the average over the selected year to compare.
                    The baseline is also based on a rolling window, so for a baseline year of 1970 with a 10-year window, it includes data from 
                    1961-1970 to compare to the rest of rolling averages. Deviations are shown as anomalies, highlighting whether it became wetter, 
                    drier, colder, or warmer compared to the baseline. This plot makes it easier to quantify the changes that have happened.
                """)

        with st.expander("Important Features"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("1. Rolling Averages")
                st.write("""
                    The maps allow you to apply rolling averages (1, 5, or 10 years) to smooth out short-term variability 
                    and highlight long-term trends. A 1-year window shows precise yearly data, while a 10-year rolling average 
                    filters out noise, making it easier to identify gradual changes like warming trends or shifts in precipitation.
                """)

            with col2:
                st.subheader("2. Hex Grids vs. Regions")
                st.write(""" 
                    **Hex Grids:** Provides a highly detailed view, dividing Finland into a grid of hexagonal cells 
                    to show local variations.  
                    **Regions:** Groups data into Finland’s 19 administrative regions, offering a broader overview 
                    suitable for regional analysis.  
                    
                    Both options let you explore Finland’s climate changes at your preferred level of detail.
                """)

            with col3:
                st.subheader("3. Interactive Map")
                st.write("""
                    The visualizations are fully interactive. Press play to see the evolution of climate data over time 
                    as an animated timeline. You can pause the animation at any point and hover over specific regions or 
                    hexagonal cells to view detailed values in a tooltip. This allows you to explore both large-scale trends 
                    and localized changes.
                """)


    def GetYearRoundMonthlyVizConfig(self):
        with st.container():
            period = st.selectbox("Rolling Average Window",self.periods)
            rolling_window = GetRollingWindow(period)
            min_year = GetMinYear(self.year_range[0],rolling_window)

        with st.container():
            self.observation = st.selectbox("Observation",self.observations)

        with st.container():
            map_type = st.radio("Map Type", ("Hexagons", "Regions"), index=0, horizontal=True)

        with st.container():
            start_year = st.slider("Start Year",min_value=min_year, max_value=self.year_range[1], value=min_year)
        
        return {"data_level":GetDataLevel(map_type), "start_year": start_year, "rolling_window": rolling_window}
    

    def GetYearlyVizConfig(self):
        with st.container():
            period = st.selectbox("Rolling Average Window",self.periods)
            rolling_window = GetRollingWindow(period)
            min_year = GetMinYear(self.year_range[0],rolling_window)

        with st.container():
            self.observation = st.selectbox("Observation",self.observations)

        with st.container():
            map_type = st.radio("Map Type", ("Hexagons", "Regions"), index=0, horizontal=True)

        with st.container():
            start_year = st.slider("Start Year",min_value=min_year, max_value=self.year_range[1], value=min_year)

        with st.container():  
            end_year = st.slider("End Year", min_value=min_year, max_value=self.year_range[1], value=self.year_range[1])
        
        return {"data_level":GetDataLevel(map_type), "start_year": start_year, "end_year": end_year,"rolling_window": rolling_window}

    
    def GetSingleMonthVizConfig(self):
        with st.container(): 
            self.observation = st.selectbox("Observation", self.observations)

        with st.container():  
            period = st.selectbox("Rolling Average Window", self.periods)
            rolling_window = GetRollingWindow(period)
            min_year = GetMinYear(self.year_range[0], rolling_window)

        with st.container():  
            map_type = st.radio("Map Type", ("Hexagons", "Regions"), index=0, horizontal=True)

        with st.container():  
            month = st.selectbox("Month", months)

        with st.container(): 
            start_year = st.slider("Start Year", min_value=min_year, max_value=self.year_range[1], value=min_year)

        with st.container():  
            end_year = st.slider("End Year", min_value=min_year, max_value=self.year_range[1], value=self.year_range[1])
        
        return {"data_level": GetDataLevel(map_type), "month": GetMonth(month), "start_year": start_year, "end_year": end_year, "rolling_window": rolling_window}
    

    def GetYearlyComparisonVizConfig(self):
        with st.container():
            self.observation = st.selectbox("Observation",self.observations)

        with st.container():
            period = st.selectbox("Rolling Average Window",self.periods)
            rolling_window = GetRollingWindow(period)
            min_year = GetMinYear(self.year_range[0],rolling_window)
        
        with st.container():
            map_type = st.radio("Map Type", ("Hexagons", "Regions"), index=0, horizontal=True)
        
        with st.container():
            comparison_year = st.slider("Comparison Period", min_value=min_year, max_value=self.year_range[1], value=min_year)

        with st.container():
            start_year = st.slider("Start Year", min_value=min_year, max_value=self.year_range[1], value=min_year)
        
        with st.container():
            end_year = st.slider("End Year", min_value=min_year, max_value=self.year_range[1], value=self.year_range[1])
        
        return {"data_level": GetDataLevel(map_type), "comparison_year": comparison_year, "start_year": start_year, "end_year": end_year, "rolling_window": rolling_window}  

    
    def GetSingleMonthComparisonVizConfig(self):
        with st.container():
            self.observation = st.selectbox("Observation",self.observations)

        with st.container():
            period = st.selectbox("Rolling Average Window",self.periods)
            rolling_window = GetRollingWindow(period)
            min_year = GetMinYear(self.year_range[0],rolling_window)
        
        with st.container():
            map_type = st.radio("Map Type", ("Hexagons", "Regions"), index=0, horizontal=True)
        
        with st.container():
            comparison_year = st.slider("Comparison Period", min_value=min_year, max_value=self.year_range[1], value=min_year)
        
        with st.container():
            month = st.selectbox("Month", months)

        with st.container():
            start_year = st.slider("Start Year", min_value=min_year, max_value=self.year_range[1], value=min_year)
        
        with st.container():
            end_year = st.slider("End Year", min_value=min_year, max_value=self.year_range[1], value=self.year_range[1])
        
        return {"data_level": GetDataLevel(map_type), "comparison_year": comparison_year, "month": GetMonth(month), "start_year": start_year, "end_year": end_year, "rolling_window": rolling_window}    

    
    def Run(self):        
        _, left, right, _ = st.columns((1,2,3,1))

        
        with left:
            for i in range(2):
                with st.container():
                    st.empty()

            
            viz_type = st.selectbox("Visualization Type", ["Yearly Climate", "Year-Round Monthly Climate (Limited to 5 Years)", "Single-Month Yearly Climate", "Yearly Climate Comparison to a Baseline", "Single-Month Yearly Climate Comparison to a Baseline"], placeholder="Yearly Climate")

            if viz_type == "Year-Round Monthly Climate (Limited to 5 Years)":
                config = self.GetYearRoundMonthlyVizConfig()
            elif viz_type == "Yearly Climate":
                config = self.GetYearlyVizConfig()
            elif viz_type == "Single-Month Yearly Climate":
                config = self.GetSingleMonthVizConfig()
            elif viz_type == "Yearly Climate Comparison to a Baseline":
                config = self.GetYearlyComparisonVizConfig()   
            elif viz_type == "Single-Month Yearly Climate Comparison to a Baseline":
                config = self.GetSingleMonthComparisonVizConfig()
    

            if st.button("Create Map"):
                if viz_type == "Year-Round Monthly Climate (Limited to 5 Years)":
                    fig = YearRoundMonthlyMapViz(self.observation).GetViz(self.db, config)
                elif viz_type == "Yearly Climate":
                    fig = YearlyMapViz(self.observation).GetViz(self.db, config)
                elif viz_type == "Single-Month Yearly Climate":
                    fig = SingleMonthMapViz(self.observation).GetViz(self.db, config)
                elif viz_type == "Yearly Climate Comparison to a Baseline":
                    fig = YearlyComparisonMapViz(self.observation).GetViz(self.db, config)
                elif viz_type == "Single-Month Yearly Climate Comparison to a Baseline":
                    fig = SingleMonthComparisonMapViz(self.observation).GetViz(self.db, config)

                st.session_state.fig = fig


        with right:
            if "fig" in st.session_state:
                st.plotly_chart(st.session_state.fig, use_container_width=True)
                
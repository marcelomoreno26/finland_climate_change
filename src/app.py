import streamlit as st

st.set_page_config(layout="wide")

if __name__ == "__main__":
    pg = st.navigation([st.Page("pages/map.py", title="Maps", icon="🗺️"),
                        st.Page("pages/time_series.py", title="Time Series",icon="📈")])
    pg.run()





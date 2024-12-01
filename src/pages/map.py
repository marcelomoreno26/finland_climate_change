import streamlit as st
from frontend import MapPage
from backend import Database

@st.cache_resource
def get_database():
    return Database()

db = get_database()
MapPage(db).Display()
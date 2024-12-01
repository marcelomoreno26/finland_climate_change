from . import st
from abc import ABC, abstractmethod


class Page(ABC):
    def __init__(self, db, title="", description=""):
        self.db = db
        self.year_range = (1960, 2023)
        self.observations = ["Snow depth","Air temperature", "Precipitation amount"]
        self.periods = ["1 Year", "5 Years", "10 Years"]
        self.title = title
        self.description = description

    @abstractmethod
    def InfoExpander(self):
        pass
   

    def Display(self):

        if self.description == "Maps":
            _, middle, _ = st.columns((1,5,1))
        elif self.description == "Time Series":
            _, middle, _ = st.columns((1,6,1))

        with middle:
            st.title(self.title)
            self.InfoExpander()
        self.Run()
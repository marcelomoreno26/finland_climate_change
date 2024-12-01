from abc import ABC, abstractmethod



class Viz(ABC):
    """
    Abstract base class for data visualizations. Initializes attributes for weather observations 
    and units, and defines required methods for querying data, adding tooltips, and getting visualizations.
    """
    def __init__(self, observation):
        self.year_range = (1960,2023)
        self.observation = observation
        self.units = self.SetUnits()

    
    def SetUnits(self):
        """
        Sets the appropriate unit based on the observation type and returns it.
        
        Returns
        -------
        str
            The unit of measurement for the observation.
        """
        if self.observation == "Snow depth":
            return "cm"
        elif self.observation == "Air temperature":
            return "°C"
        elif self.observation == "Precipitation amount":
            return "mm"

    
    @abstractmethod
    def Query():
        """
        Abstract method for querying data specific to the visualization.

        Parameters
        ----------
        args, kwargs
            The required parameters for the query may vary by visualization type.
        
        Returns
        -------
        pandas.DataFrame
            Dataframe containing the queried data.
        """
        pass
       
    
    @abstractmethod
    def AddTooltip():
        """
        Abstract method to add tooltips for visualizations.

        Parameters
        ----------
        args, kwargs
            The required parameters for adding tooltips may vary.
        
        Returns
        -------
        pandas.DataFrame
            The dataframe with an added 'tooltip' column.
        """
        pass
    
    
    @abstractmethod
    def GetViz(self):
        """
        Abstract method for generating the visualization.

        Parameters
        ----------
        args, kwargs
            The required parameters for generating the visualization may vary.
        
        Returns
        -------
        plotly.graph_objs.Figure
            The generated visualization.
        """
        pass
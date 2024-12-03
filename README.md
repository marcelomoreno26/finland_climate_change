# Finland Climate Change - Interactive Visualization

[Explore the app here](https://finland-climate-change.streamlit.app/)

## Motivation

When I arrived in Finland as an exchange student, one of my first questions was: “When does the snow usually fall and stay?” The response was usually along the lines of “Recently because of climate change, it is hard to tell”. The responses highlighted a broader issue: seasons are becoming increasingly unpredictable in countries like Finland, where winter has always been a defining feature. Understanding climate change goes beyond snowfall; it’s about recognizing the impacts on daily life, from shifting temperatures to varying seasonal weather patterns. These changes directly affect citizens and visitors alike, making it crucial to explore and understand the effect climate change has had in recent times. 

With this project, I aim to create an interactive visualization that helps users understand and explore how climate change is changing the Finnish environment, focusing on the weather patterns over the past 60+ years.

## Project Structure

The project is structured to separate different aspects of data retrieval, preprocessing, and the Streamlit app development. Here's an overview of the directory structure:


```
root
├── .devcontainer/               
├── .streamlit/                    
├── data_retrieval/               
│   └── raw_data/                 
├── preprocessing/                
│   └── processed_data/           
├── data/                         
│   └── geodata/                  
├── src/                          
│   ├── pages/                    
│   ├── frontend/                 
│   ├── backend/                  
│   ├── app.py                    
└── README.md                     
└── requirements.txt              

```

**Data Retrieval (`data_retrieval`)**: This directory contains the scripts to fetch daily weather data from the Finnish Meteorological Institute's API. The data covers a 60+ year span, and while initially intended for all daily data, it was later realized that using monthly data would have been more efficient. The API is not directly used in the app, as fetching all the required historical data takes too long.

**Preprocessing (`preprocessing`)**: This folder holds the scripts for processing the raw data. It includes steps to aggregate weather data by year, month, region, and hexagonal grid cells. The output data is used for visualizations and further analysis in the app.

**Processed Data (`data`)**: Contains the data in its processed form, ready for use in the Streamlit app. The data includes weather information aggregated by hexagonal grids and regions. The `geodata` subfolder holds the geographical data for the regions and hexagons used to display the weather data on maps.

**Streamlit App (`src`)**: This folder contains the source code for the Streamlit app:
   - `pages/`: Contains the scripts for different pages in the app.
   - `frontend/`: Scripts that handle the frontend logic, which displays website with the filters and renders visualizations to the user.
   - `backend/`: Scripts that process the data and create visualizations for the app.
   - `app.py`: The main script that runs the Streamlit app, bringing together all the frontend and backend components.


## Data Source

The data used in this project is sourced from the Finnish Meteorological Institute (FMI) Open Data interface, which provides free access to a variety of datasets, including weather, sea, and air quality observations. The data is available in machine-readable format, though some technical skills and meteorological knowledge may be required to utilize it effectively. 

For more details on the available datasets, visit the [FMI Open Data website](https://en.ilmatieteenlaitos.fi/open-data).

For Python users, the [FMI Open Data API documentation](https://github.com/pnuu/fmiopendata) provides resources for accessing and using the data programmatically.

### Deployment

The Streamlit app has been deployed and is accessible through the following link:

[Finland Climate Change - Interactive Visualization](https://finland-climate-change.streamlit.app/)

Feel free to explore how climate change is affecting Finnish weather patterns through this interactive tool!

 

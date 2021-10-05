import pandas as pd
import geopandas as gp
import folium as fo
import streamlit as st
from streamlit_folium import folium_static
import altair as alt
import pydeck as pdk
import numpy as np

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns(2)

with row1_1:
	date_select = st.selectbox("select day of pick up",("Jan. 1, 2019", "Jan. 2, 2019","Jan. 3, 2019","Jan. 4, 2019","Jan. 5, 2019"))
	hour_selected = st.slider("Select hour of pickup", 0, 23)
with row1_2:
	st.title("Streamlit web map")

# LOADING DATA
DATE_TIME = "date/time"
jan12019 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190101.csv")
jan22019 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190102.csv")
jan32019 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190103.csv")
jan42019 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190104.csv")
jan52019 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190105.csv")

st.title('Streamlit Buffer Example')
add_select = st.sidebar.selectbox("What basemap do you want to see?",("OpenStreetMap", "Stamen Terrain","Stamen Toner"))



#SELECT DATA ACCORDING TO date_select
if date_select == "Jan. 1, 2019" :
  DATA_URL = jan12019
elif date_select == "Jan. 2, 2019" :
  DATA_URL = jan22019
elif date_select == "Jan. 3, 2019" :
  DATA_URL = jan32019
elif date_select == "Jan. 4, 2019" :
  DATA_URL = jan42019
elif date_select == "Jan. 5, 2019" :
  DATA_URL = jan52019

@st.cache(persist=True)
def load_data_stop(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data = data[['timestop','latstop','lonstop']].copy()
    data = data.rename(columns = {'timestop': 'Date/Time', 'latstop': 'Lat', 'lonstop': 'Lon'}, inplace = False)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
    return data

data = load_data_stop(100000)

# CREATING FUNCTION FOR MAPS
def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))


# FILTERING DATA BY HOUR SELECTED
data = data[(data[DATE_TIME].dt.hour == hour_selected) & (data[DATE_TIME].dt.year == 2019)]

#create map
longitude = 100.819200
latitude = 19.331900
zoom_level = 12

st.write("**web map**")
map(data, 100.819200 ,19.331900 , zoom_level)

# FILTERING DATA FOR THE HISTOGRAM
filtered = data[
    (data[DATE_TIME].dt.hour >= hour_selected) & (data[DATE_TIME].dt.hour < (hour_selected + 1))
    ]
		
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "stop": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")
st.write("histrogram")
st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("stop:Q"),
        tooltip=['minute', 'stop']
    ).configure_mark(
        opacity=0.5,
        color='red'
    ), use_container_width=True)

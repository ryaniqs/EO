import streamlit as st
import pandas as pd
import requests
from PIL import Image, ImageDraw

# Define the Streamlit app
@st.cache
def load_data():
    # Call the Planet Explorer API to retrieve the most recent images
    url = "https://api.planet.com/explorer/v1/quick-search"
    headers = {"Authorization": "PLAK084e2f517ee848519bfa86a3370ad434"}
    params = {
        "item_types": ["PSScene4Band"],
        "geom": "POLYGON((-84.9017 39.7774, -84.9017 39.8257, -84.8138 39.8257, -84.8138 39.7774, -84.9017 39.7774))",
        "acquired": "2022-04-11T00:00:00Z/2022-04-12T23:59:59Z",
        "limit": 2,
    }
    response = requests.get(url, headers=headers, params=params).json()

    # Transform the API response into a DataFrame
    data = pd.json_normalize(response["features"])
    data = data[["id", "properties.acquired", "properties.item_type", "geometry"]]
    data["properties.acquired"] = pd.to_datetime(data["properties.acquired"])

    return data

# Load the data
data = load_data()

# Display the images in the Streamlit app
st.header("Richmond, Indiana")
st.subheader("April 11-12, 2022")

with st.spinner("Loading images..."):
    images = []
    for i in range(len(data)):
        # Call the Planet API to retrieve the image
        url = f"https://api.planet.com/v1/item-types/{data.iloc[i]['properties.item_type']}/items/{data.iloc[i]['id']}/assets"
        headers = {"Authorization": "api-key YOUR_API_KEY_HERE"}
        params = {"asset_type": "visual"}
        response = requests.get(url, headers=headers, params=params).json()

        # Download and resize the image
        img_url = response["visual"]["location"]
        img = Image.open(requests.get(img_url, stream=True).raw)
        img = img.resize((640, 640))
        images.append(img)

    # Create and display the GIF
    images[0].save("richmond.gif", save_all=True, append_images=images[1:], duration=1000, loop=0)
    st.image("richmond.gif")

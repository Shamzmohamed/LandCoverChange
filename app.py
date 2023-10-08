import os
import re
import folium
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy.ma as ma
import rioxarray
import streamlit as st
from streamlit_folium import folium_static

st.title("Land Cover Change")
st.write("Select the specified path of dataset for the year 1 and year 2 from the local directory")
st.sidebar.info("About:\n"
                "This dashboard allows users to visualise the landcover changes of two different years from landsat 8 images\n"
                " It shows \n"
                "- Vegetation Change\n"
                "- Built-up Change\n"
                "- Waterbody Change\n"
                "- Soil Adjusted Change for the corresponding dataset.\n")
st.sidebar.info("""Author
 - [Mohamed Shamsudeen](mailto:shamsudeen.m@uni-muenster.de)""")


# Add the input fields to the first column
def main():
    # to open the bands having B in its name
    def open_year_bands(year_path):
        year_bands = {}
        for file_name in os.listdir(year_path):
            match = re.search(r'B(\d)', file_name)
            if match:
                year_bands[match.group(1)] = os.path.join(year_path, file_name)

        bands = {}
        for i in range(1, 8):
            bands[str(i)] = rioxarray.open_rasterio(year_bands.get(str(i), ''), masked=True)

        return bands

    # folium parameters
    def get_map_parameters(data_array):
        # Get bounds and calculate center location
        bounds = data_array.rio.bounds()
        minx, miny, maxx, maxy = bounds
        location = [(miny + maxy) / 2, (minx + maxx) / 2]
        map_bounds = [[miny, minx], [maxy, maxx]]
        return location, map_bounds

    # indices calculation
    def calculate_ndvi(xr_data):
        ndvi = (xr_data['5'] - xr_data['4']) / (xr_data['5'] + xr_data['4'])
        return ndvi

    def calculate_ndwi(xr_data):
        ndwi = (xr_data['3'] - xr_data['5']) / (xr_data['3'] + xr_data['5'])
        return ndwi

    def calculate_ndbi(xr_data):
        ndbi = (xr_data['6'] - xr_data['5']) / (xr_data['6'] + xr_data['5'])
        return ndbi

    def calculate_savi(xr_data, L=0.5):
        savi = ((xr_data['5'] - xr_data['4']) / (xr_data['5'] + xr_data['4'] + L)) * (1 + L)
        return savi

    #  to make the array plotable
    def color(ndvi_array, cmap='RdYlGn'):
        # Mask invalid values
        ndvi_array = ndvi_array.values
        ndvi_masked = ma.masked_invalid(ndvi_array)
        # Normalize the data
        normed_data = (ndvi_masked - ndvi_masked.min()) / (ndvi_masked.max() - ndvi_masked.min())
        # Apply the colormap
        cm = plt.cm.get_cmap(cmap)
        colored_data = cm(normed_data)
        # Remove the extra dimension from the array
        colored_data = colored_data.squeeze(axis=0)
        return colored_data

    def create_masked_color_data(change, threshold, colors_list):
        # Mask the invalid data
        masked_data = ma.masked_invalid(change)
        # Create a binary mask based on the threshold value
        mask = (masked_data > threshold).astype(float)
        # Set the colors for the two classes
        cmap = colors.ListedColormap(colors_list)
        # Create a color map for the binary mask
        bounds = [0, 0.5, 1]
        norm = colors.BoundaryNorm(bounds, cmap.N)
        # Apply the color map to the mask
        masked_data_colors = cmap(norm(mask))
        # Remove the first dimension if present
        masked_data_colors = masked_data_colors.squeeze(axis=0)
        return masked_data_colors

    # to create changes folium map
    def create_map(Cndvi, Y1ndvi, Y2ndvi, name1, name2, name3, opacity=0.7, zoom_start=11):
        m = folium.Map(location=location, zoom_start=zoom_start)
        fg_data = folium.FeatureGroup(name=name1, show=True)
        folium.raster_layers.ImageOverlay(Cndvi, opacity=opacity, bounds=map_bounds).add_to(fg_data)

        fg_data2 = folium.FeatureGroup(name=name2, show=False)
        folium.raster_layers.ImageOverlay(Y1ndvi, opacity=opacity, bounds=map_bounds,
                                          control=False).add_to(fg_data2)

        fg_data3 = folium.FeatureGroup(name=name3, show=False)
        folium.raster_layers.ImageOverlay(Y2ndvi, opacity=opacity, bounds=map_bounds, control=False).add_to(fg_data3)
        fg_data.add_to(m)
        fg_data2.add_to(m)
        fg_data3.add_to(m)
        folium.LayerControl().add_to(m)
        return m

    # Input path field
    year1_path = st.text_input('Year 1 Path')
    year2_path = st.text_input('Year 2 Path')
    session_state = st.session_state
    # open bands after input
    if year1_path and year2_path:  # Check if input is not empty
        year1_bands = open_year_bands(year1_path)
        year2_bands = open_year_bands(year2_path)

        session_state.year1_bands = year1_bands
        session_state.year2_bands = year2_bands

        # calculat indices for both years
        Y1ndvi = calculate_ndvi(session_state.year1_bands)
        Y2ndvi = calculate_ndvi(session_state.year2_bands)
        Y1ndbi = calculate_ndbi(session_state.year1_bands)
        Y2ndbi = calculate_ndbi(session_state.year2_bands)
        Y1ndwi = calculate_ndwi(session_state.year1_bands)
        Y2ndwi = calculate_ndwi(session_state.year2_bands)
        Y1savi = calculate_savi(session_state.year1_bands)
        Y2savi = calculate_savi(session_state.year2_bands)
        location, map_bounds = get_map_parameters(Y1ndvi)

        # create colormask for all
        threshold = 0
        colored_Y1ndvi = color(Y1ndvi, cmap='RdYlGn')
        colored_Y2ndvi = color(Y2ndvi, cmap='RdYlGn')
        colored_Y1ndwi = color(Y1ndwi, cmap='PuBu')
        colored_Y2ndwi = color(Y2ndwi, cmap='PuBu')
        colored_Y1ndbi = color(Y1ndbi, cmap='PuRd')
        colored_Y2ndbi = color(Y2ndbi, cmap='PuRd')
        colored_Y1savi = color(Y1savi, cmap='RdYlBu')
        colored_Y2savi = color(Y2savi, cmap='RdYlBu')

        # visualise changes with this color list
        colors_list = ['darkblue', 'pink']

        # Compute NDVI change
        ndviChange = Y1ndvi - Y2ndvi
        # Create a color map for the binary mask
        cndvi  = create_masked_color_data(ndviChange, threshold, colors_list)
        # create Vegetataion change map
        V = create_map(cndvi, colored_Y1ndvi, colored_Y2ndvi, 'Vegetation Change ', 'Year 1 NDVI', 'Year 2 NDVI')

        # Compute NDBI change
        ndbi_change = Y1ndbi - Y2ndbi
        # Create a color map for the binary mask
        Cndbi = create_masked_color_data(ndbi_change, threshold, colors_list)
        # NDBI folium feature group
        B = create_map(Cndbi, colored_Y1ndbi, colored_Y2ndbi, 'Buildup Change ', 'Year 1 NDBI', 'Year 2 NDBI')

        # Compute SAVI change
        savi_Change = Y1savi - Y2savi
        # Create a binary mask based on the threshold value
        # mask_savi = create_binary_mask(savi_Change, threshold)
        # Create a color map for the binary mask
        Csavi = create_masked_color_data(savi_Change, threshold, colors_list)
        # SAVI folium feature group
        S = create_map(Csavi, colored_Y1savi, colored_Y2savi, 'Soil Change ', 'Year 1 SAVI', 'Year 2 SAVI')

        # Compute NDWI change
        ndwi_Change = Y1ndwi - Y2ndwi
        # Create a color map for the binary mask
        cndwi = create_masked_color_data(ndwi_Change, threshold, colors_list)
        # NDWI folium feature group
        W = create_map(cndwi, colored_Y1ndwi, colored_Y2ndwi, 'Water Change ', 'Year 1 NDWI', 'Year 2 NDWI')
        # store all in session state
        session_state.maps = {}
        session_state.maps['Vegetation change'] = V
        session_state.maps['Waterbody change'] = W
        session_state.maps['Soil moisture change'] = S
        session_state.maps['Builtup change'] = B
        subpage(session_state, colors_list)


def subpage(session_state, colors_list):
    selection = st.selectbox('Select a map',
                             ['Vegetation change', 'Waterbody change', 'Soil moisture change', 'Builtup change'])

    folium_static(session_state.maps[selection])

    labels = ['Change', 'No change']

    # Create a custom legend
    fig, ax = plt.subplots()
    fig.set_size_inches(.01, .01)  # Adjust figure size
    for i, color in enumerate(colors_list):
        x_pos = i - 0.5 if i == 0 else i + 0.5
        ax.bar(x_pos, 0, color=color, label=labels[i])
    ax.axis('off')
    ax.legend(loc='center', ncol=2,
              fontsize='small')
    st.pyplot(fig, dpi=500)


if __name__ == '__main__':
    main()

# Land Cover Change

## Description : 
The goal of the project is to visualize the Spatio-temporal changes of the landsurface for two years. Currently, we have found the landsurface change for Münster, Germany for the years 2013 and 2022. We created an interactive web application using the Streamlit and Folium libraries. The application takes input paths for two directories, each containing raster image files representing different spectral bands of satellite imagery for two years. The user can select which vegetation index to calculate and visualize and can also adjust a threshold value for creating a binary mask. The NDVI (Normalized Difference Vegetation Index), NDWI (Normalized Difference Water Index), NDBI (Normalized Difference Built-up Index), and SAVI (Soil Adjusted Vegetation Index) are calculated using the specified spectral bands. The calculated vegetation index is then used to create a color-coded raster image, and the image is displayed on an interactive map using the Folium library. The color-coded image is also overlaid with a binary mask, which can be adjusted by the user using the threshold slider.

## Dataset
- You can use Landsat data for any area of interest in this dashboard.
- We used [Google Earth Engine](https://code.earthengine.google.com/) to collect the cloud-free data of Landsat 8 (30m spatial resolution). You can find the Javascript code to download the dataset from GEE for Münster, Germany.
- We used 2013 and 2022 Landsat 8 data which is in "sample Landsat files" directory
## Requirements
    conda env create -f requirements.yml

## To Run
    streamlit run app.py
# Gaia DR3 Visualization Tool
This repo show an example of how visualizing data using python and building a bokeh server to add some basic interactions. The data come from the Gaia Data Release 3, and it can be downloaded using the notebook share in this repository.

![Tool example](https://github.com/raul-santovena/gaia-dr3-visualization/blob/main/gif_example.gif)

This tool show several things:
 - In the upper left corner, it displays a [HR diagram](https://en.wikipedia.org/wiki/Hertzsprung%E2%80%93Russell_diagram) about the downloaded stars.
 - In the upper right corner shows both the [BP-RP Spectra](https://www.cosmos.esa.int/web/gaia/photometric-instrument) (using coefficients) and [RVS Spectra](https://www.cosmos.esa.int/web/gaia/radial-velocity-spectrometer).
 - The bottom of the tool ilustrates the application of the T-SNE algotithm, applied respectively to the BP-RP and RVS spectra, where the data were reduced to a two-dimensional space.
 
Using the [bokeh](https://docs.bokeh.org/en/latest/) library, some interactions can be performed, such as choosing between different color representations based on temperature, gravity, or metallicity; represent the size of the objects using their absolute magnitude, or select specific data to highlight their relationships.


## Instructions
### Set up the environment
First of all, it is advisable to create a virtual environment.

Using conda:

    conda create -n gaia-dr3-visualization python=3.7
    conda activate gaia-dr3-visualization
  
Now, you can install all the required libraries running the command below:

    conda install -c conda-forge numpy pandas matplotlib jupyterlab scikit-learn astroquery bokeh
    
If you want to run the last section to visualize a dimensionality reduction in 3d, it is required to install also plotly:

    conda install -c plotly plotly
    
You may also need to install the ipywidgets package to visualize the figures correctly in a jupyter notebook:
    conda install ipywidgets
    
### Run the jupyper notebook
Running the notebook located in the repo, you can see a simple example of 1) downloading data from Gaia Arquive using ADQL, and also downloading spectra information stored in Gaia Datalink (more info on [Datalink Products](https://www.cosmos.esa.int/web/gaia-users/archive/datalink-products)); 2) saving the downloaded data to be used later by the server; 3) running the t-sne algorithm with the BP-RP and RVS Spectra and 4) displaying the HR-diagram of the selected objects, their RVS and BP-RP spectra, and the 2D representation of the application of t-sne to both types of spectra.

### Run the bokeh server:
To build and run the server you can run the following command from Anaconda Powershell, or use a code editor like VS Code (this command must be run from the root folder of the repository):

    bokeh serve --show main.py 
    
You can also run the server from the parent directory using the command below:

    bokeh serve --show gaia-dr3-visualization
    
NOTE: It is required to run the section 1 of the notebook at least once to download the data for the server
    

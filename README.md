# HadUK-Grid_API

**Script to download the weather data from HadUK-Grid using Python3**

**Installation:**

```bash
pip3 install tqdm cf matplotlib numpy calendar optparse pandas
```
or 
```bash
conda install tqdm cf matplotlib numpy calendar optparse pandas 
```

**Usage:**

```
****************************************************************************************************************************
API_HadUKGrid_data.py: Script to download the weather data from HadUK-Grid
****************************************************************************************************************************
Usage: API_HadUKGrid_data.py [options] 

Options:
  -h, --help            show this help message and exit
  -u USERNAME, --username=USERNAME
                        Please use your account id for HadUK-Grid
  -p PASSWORD, --password=PASSWORD
                        Please use your account password for HadUK-Grid
  -v VARIABLE, --variable=VARIABLE
                        Type of the desired data: tasmax for Maximum air
                        temperature; tasmin Minimum air temperature; tas: Mean
                        air temperature; rainfall: Precipitation; sun:
                        Sunshine duration; sfcWind: Mean wind speed at 10 m;
                        psl: Mean sea level pressure; hurs: Mean relative
                        humidity; pv: Mean vapour pressure; groundfrost: Days
                        with ground frost; snowLying: Snow lying
  -t TEMPORAL, --temporal=TEMPORAL
                        Temporal resolution: [mon] for monthly or [day] for
                        daily
  -i DATE1, --date1=DATE1
                        First date in YYYY-MM-DD format
  -j DATE2, --date2=DATE2
                        First date in YYYY-MM-DD format
  -m MODE, --mode=MODE  Format of saved data: to .[tif] image or .[txt] file
  -r ROI, --ROI=ROI     Region Of Interest: can be a point [lat,lon] or a box
                        [S,N,W,E]. The box is mandatory for .tif mode
  -w WRITEDIRECTORY, --writedirectory=WRITEDIRECTORY
                        Directory of the downloaded files: default is [./tmp]
                        (optional)
  -o OUTPUTDIRECTORY, --outputdirectory=OUTPUTDIRECTORY
                        Directory of the outputs: default is [.] (optional)
  -c CLEAN, --clean=CLEAN
                        Clean the tmp files: default is [True], [or False]
                        (optional)
  -n NAME, --name=NAME  Prefixe name of output files (optional)
  -s SPATIAL, --spatial=SPATIAL
                        Spatial resolution of data: default is [1km] [1km,
                        5km, 12km, 25km, 60km] (optional)
  -f FIGURE, --figure=FIGURE
                        Generation of quicklook figure: default is n [y or n]
                        (optional)
 ```
 
 **If the tif images are desired:** (TO DO)
 ```bash
 API_HadUKGrid_data.py -u username -p password -v rainfall -t mon -i 2015-01-15 -j 2022-12-31 -m tif -r 52.15,52.57,-3.94,-2.9
 ```
 
 **If the txt file is desired:**
 1. Using a ROI (the average values will be computed):
 ```bash
 API_HadUKGrid_data.py -u username -p password -v rainfall -t mon -i 2015-01-15 -j 2022-12-31 -m txt -r 52.15,52.57,-3.94,-2.9
 ```
 2. Using a point (nearest value):
 ```bash
 API_HadUKGrid_data.py -u username -p password -v rainfall -t mon -i 2015-01-15 -j 2022-12-31 -m txt -r 52.15,-3.94
 ```
 
 **PLEASE SEE [https://rmets.onlinelibrary.wiley.com/doi/full/10.1002/gdj3.78](https://rmets.onlinelibrary.wiley.com/doi/full/10.1002/gdj3.78) for references.**
 
 **Author:**
 
 Alexis Hrysiewicz (UCD / iCRAG)

#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

##########################################################################################
# Header information 
###########################################################################

"""API_HadUKGrid_data.py: Script to download the weather data from HadUK-Grid"""

__author__ = "Alexis Hrysiewicz"
__copyright__ = "Copyright 2022"
__credits__ = ["Alexis Hrysiewicz"]
__license__ = "GPLV3"
__version__ = "0.5.0"
__maintainer__ = "Alexis Hrysiewicz"
__status__ = "Production"
__date__ = "Aug. 2022"

print("****************************************************************************************************************************")
print("API_HadUKGrid_data.py: Script to download the weather data from HadUK-Grid")
print("****************************************************************************************************************************")

###########################################################################
# Python packages
###########################################################################
import sys
import os
from tqdm import tqdm
import cf
from matplotlib import path
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
import numpy as np
from datetime import datetime, timezone, timedelta
from calendar import monthrange
import optparse
from ftplib import FTP
import pandas as pd

cur_dir = os.getcwd()

###########################################################################
# Server Information 
###########################################################################
ver=''

###########################################################################
# Definition of functions and classes
###########################################################################
class OptionParser (optparse.OptionParser):
    def check_required(self, opt):
        option = self.get_option(opt)
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)

def date_range_list(start_date, end_date):
    date_list = []
    curr_date = start_date
    while curr_date <= end_date:
        date_list.append(curr_date)
        curr_date += timedelta(days=1)
    return date_list

###########################################################################
# Definition of options
###########################################################################
if len(sys.argv) < 2:
    prog = os.path.basename(sys.argv[0])
    print("example: python3 %s -u username -p password -v rainfall -t mon -i 2020-01-01 -j 2020-12-31 -m txt -r 51.51,-0.11 (-w ./tmp) (-o .) (-c True) (-n '')" %
          sys.argv[0])
    sys.exit(-1)
else:
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)
    parser.add_option("-u", "--username", dest="username", action="store", type="string", default='username', 
        help="Please use your account id for HadUK-Grid")                   
    parser.add_option("-p", "--password", dest="password", action="store", type="string", default='password', 
        help="Please use your account password for HadUK-Grid")
    parser.add_option("-v", "--variable", dest="variable", action="store", type="string", default='none', 
        help="Type of the desired data: tasmax for Maximum air temperature; tasmin Minimum air temperature; tas: Mean air temperature; rainfall: Precipitation; sun: Sunshine duration; sfcWind: Mean wind speed at 10 m; psl: Mean sea level pressure; hurs: Mean relative humidity; pv: Mean vapour pressure; groundfrost: Days with ground frost; snowLying: Snow lying")
    parser.add_option("-t", "--temporal", dest="temporal", action="store", type="string", default='none', 
        help="Temporal resolution: [mon] for monthly or [day] for daily")    
    parser.add_option("-i", "--date1", dest="date1", action="store", type="string", default='none', 
        help="First date in YYYY-MM-DD format")    
    parser.add_option("-j", "--date2", dest="date2", action="store", type="string", default='none', 
        help="First date in YYYY-MM-DD format") 
    parser.add_option("-m", "--mode", dest="mode", action="store", type="string", default='none', 
        help="Format of saved data: to .[tif] image or .[txt] file")
    parser.add_option("-r", "--ROI", dest="ROI", action="store", type="string", default='0,0', 
        help="Region Of Interest: can be a point [lat,lon] or a box [S,N,W,E]. The box is mandatory for .tif mode")
    parser.add_option("-w", "--writedirectory", dest="writedirectory", action="store", type="string", default='./tmp', 
        help="Directory of the downloaded files: default is [./tmp] (optional)")
    parser.add_option("-o", "--outputdirectory", dest="outputdirectory", action="store", type="string", default='.', 
        help="Directory of the outputs: default is [.] (optional)")   
    parser.add_option("-c", "--clean", dest="clean", action="store", type='string', default='n', 
        help="Clean the tmp files: default is [True], [or False] (optional)")   
    parser.add_option("-n", "--name", dest="name", action="store", type="string", default='', 
        help="Prefixe name of output files (optional)")  
    parser.add_option("-s", "--spatial", dest="spatial", action="store", type="string", default='1km', 
        help="Spatial resolution of data: default is [1km] [1km, 5km, 12km, 25km, 60km] (optional)")  
    parser.add_option("-f", "--figure", dest="figure", action="store", type="string", default='n', 
        help="Generation of quicklook figure: default is n [y or n] (optional)")  

    (options, args) = parser.parse_args()

###########################################################################
# Checking of options
###########################################################################
error=0
if options.username == 'username': 
    print("ERROR: please use a valid username for -u option")
    error=1

if options.password == 'password': 
    print("ERROR: please use a valid password for -p option")
    error=1

if not options.variable in ['tasmax', 'tasmin', 'tas', 'rainfall', 'sun', 'sfcWind', 'psl', 'hurs', 'pv', 'groundforst', 'snowLying']:
    print("ERROR: please use a valid variable name for -v option [tasmax, tasmin, tas, rainfall, sun, sfcWind, psl, hurs, pv, groundforst, snowLying]")
    error=1

if not options.temporal in ['mon', 'day']:
    print("ERROR: please use a valid temporal resolution name for -t option [mon, day]")
    error=1

# # Check the consistency 
# if options.variable in ['tas','sun', 'sfcWind', 'psl', 'hurs', 'pv', 'groundforst', 'snowLying'] and options.temporal == 'day':
#     print("ERROR: [%s] option is not possible with the [%s] temporal resolution option" % (options.variable, options.temporal) )
#     sys.exit(-1)

# Check the dates
try:
    date1 = datetime.strptime(options.date1, '%Y-%m-%d')
except: 
    print("ERROR: please use a correct date [YYYY-MM-DD] for -i option")
    sys.exit(-1)
try:
    date2 = datetime.strptime(options.date2, '%Y-%m-%d')
except: 
    print("ERROR: please use a correct date [YYYY-MM-DD] for -j option")
    sys.exit(-1)

if date1 > date2: 
    print("ERROR: The first date must be older than the second date")
    sys.exit(-1)

if not options.mode in ['tif', 'txt']:
    print("ERROR: please use a valid mode name for -m option [tif or txt]")
    error=1

if options.ROI == '0,0':
    print("ERROR: please use a valid Region Of Interest: can be a point [lat,lon] or a box [S,N,W,E]. The box is mandatory for .tif mode")
    error=1
else: 
    ROI = options.ROI.split(',')
    if len(ROI) == 2: 
        lonpt = ROI[1]
        latpt = ROI[0]
        if not lonpt.replace('.','',1).replace('-','',1).isnumeric() or not latpt.replace('.','',1).replace('-','',1).isnumeric():
            print("ERROR: Please use numeric values of -r option: [lon,lat]")
            sys.exit(-1)
        else: 
            if not (float(lonpt) >= -180 and float(lonpt) <= 180) or not (float(latpt) >= -90 and float(latpt) <= 90):
                print("ERROR: Please use correct values of -r option: [lon,lat]")
                sys.exit(-1)
            else: 
                ROI = [float(latpt),float(lonpt)]
    elif len(ROI) == 4:
        S = ROI[0]
        N = ROI[1]
        W = ROI[2]
        E = ROI[3]
        if not S.replace('.','',1).replace('-','',1).isnumeric() or not N.replace('.','',1).replace('-','',1).isnumeric() or not W.replace('.','',1).replace('-','',1).isnumeric() or not E.replace('.','',1).replace('-','',1).isnumeric():
            print("ERROR: Please use numeric values of -r option")
            sys.exit(-1) 
        else: 
            if not (float(W) >= -180 and float(W) <= 180) or not (float(E) >= -180 and float(E) <= 180) or not (float(S) >= -90 and float(S) <= 90) or not (float(N) >= -90 and float(N) <= 90):
                print("ERROR: Please use correct values of -r option: a box [S,N,W,E]")
                sys.exit(-1)
            elif float(W) >= float(E) or float(S) >= float(N): 
                print("ERROR: Please use correct values of -r option: a box [S,N,W,E] ")
                sys.exit(-1)
            else: 
                ROI = [float(S),float(N),float(W),float(E)]
    else:
        print("ERROR: please use a valid Region Of Interest: can be a point [lat,lon] or a box [S,N,W,E]. The box is mandatory for .tif mode")
        sys.exit(-1)

if len(ROI) == 2 and options.mode == 'tif':
    print("ERROR: the point selection for -r option is not compatible with -m tif")
    sys.exit(-1)      

if not options.clean in ['y','n']:
    print("ERROR: please use a correct clean option (-c) [y or n]")
    sys.exit(-1)

if not options.spatial in ['1km', '5km', '12km', '25km', '60km']:
    print("ERROR: please use a correct spatial resolution option (-s) [[1km, 5km, 12km, 25km, 60km]]")
    error = 1

if not options.figure in ['y', 'n']:
    print("ERROR: please use a correct figure option (-f) [y or n]")
    error = 1
else:
    if options.figure == 'y' and options.mode == 'tif':
        print("ERROR: the -f option (y) is not compatible with -m option (tif)")
        error = 1

if error == 1:
    sys.exit(-1)

###########################################################################
# Creation of work directory
###########################################################################
if not options.writedirectory == "." or not options.writedirectory == "" or not options.writedirectory == "/":
    if not os.path.isdir(options.writedirectory):
        os.mkdir(options.writedirectory)
else:
    print("ERROR: please select a good work directory")
    sys.exit(-1)

if not options.outputdirectory == "." or not options.outputdirectory == "":
    if not os.path.isdir(options.outputdirectory):
        os.mkdir(options.outputdirectory)
if options.outputdirectory == "":
    options.outputdirectory == "."

###########################################################################
# Creation of the list of data
###########################################################################
print('First connection to identify the list of data:')

ftp_hadUK_Grid = FTP('ftp.ceda.ac.uk')
ftp_hadUK_Grid.encoding = "utf-8"
ftp_hadUK_Grid.login(user=options.username,passwd=options.password)
ftp_hadUK_Grid.cwd('badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid')

# Find the version
version = ftp_hadUK_Grid.nlst()
if ver == '':
    version_grid = version[-1]
else:
    if ver in version:
        version_grid = ver
    else:
        ftp_hadUK_Grid.quit()
        print("ERROR: The desired version of HadUK-Grid does not exist")
        sys.exit(-1)
print("\tThe selected version is %s" % (version_grid))

# Find the spatial resolution
ftp_hadUK_Grid.cwd(version_grid)
list_res = ftp_hadUK_Grid.nlst()
if options.spatial in list_res:
    spt_res = options.spatial
else:
    ftp_hadUK_Grid.quit()
    print("ERROR: The desired spatial resolution of HadUK-Grid does not exist")
    sys.exit(-1)
print("\tThe selected spatial resolution is %s" % (spt_res))

# Find the variable
ftp_hadUK_Grid.cwd(spt_res)
list_variable = ftp_hadUK_Grid.nlst()
if options.variable in list_variable:
    variable = options.variable
else:
    ftp_hadUK_Grid.quit()
    print("ERROR: The desired variable of HadUK-Grid does not exist for these parameters")
    sys.exit(-1)
print("\tThe selected variable is %s" % (variable))

# Find the temporal resolution
ftp_hadUK_Grid.cwd(variable)
list_type = ftp_hadUK_Grid.nlst()
if options.temporal in list_type:
    temp_res = options.temporal
else:
    ftp_hadUK_Grid.quit()
    print("ERROR: The desired temporal resolution of HadUK-Grid does not exist for these parameters")
    sys.exit(-1)
print("\tThe selected temporal resolution is %s" % (temp_res))

# Find the update
ftp_hadUK_Grid.cwd(temp_res)
list_update = ftp_hadUK_Grid.nlst()
update_version = list_update[-1]
print("\tThe selected update version is %s" % (update_version))

# List the available files
ftp_hadUK_Grid.cwd(update_version)
list_file_ftp = ftp_hadUK_Grid.nlst()

# Quit the FTP
ftp_hadUK_Grid.quit()
print("\tThe list of available data has been found.")

###########################################################################
# Generation of the list of data which must be downloaded
###########################################################################
# Conversion of date to file name
date1 = datetime.strptime(options.date1, '%Y-%m-%d')
date2 = datetime.strptime(options.date2, '%Y-%m-%d')

list_year = np.arange(date1.year,date2.year+1,1)

list_name_date = []
if temp_res == 'mon':
    for yi in list_year:
        list_name_date.append('%d01-%d12' % (yi,yi))
elif temp_res == 'day':
    if len(list_year) == 1:
        list_month = np.arange(date1.month,date2.month+1,1)
        for mi in list_month:
            num_days = monthrange(list_year[0], mi)[1]
            list_name_date.append('%d%02d01-%d%02d%d' % (list_year[0],mi,list_year[0],mi,num_days))
    elif len(list_year) > 1:
        date_list = date_range_list(date1, date2)
        for di in date_list:
            num_days = monthrange(di.year, di.month)[1]
            list_name_date.append('%d%02d01-%d%02d%d' % (di.year,di.month,di.year,di.month,num_days))
        list_name_date = np.unique(list_name_date)

# Check the available data
print('Check the available data:')
list_of_files = []
for datai in list_name_date:
    name1 = "%s_hadukgrid_uk_%s_%s_%s.nc" %(variable,spt_res,temp_res,datai)
    print('\tFor the file: %s' %(name1))
    if name1 in list_file_ftp:
        print('\t\tFOUND')
        list_of_files.append(name1)
    else:
        print('\t\tNOT AVAILABLE')

if not list_of_files:
    print('ERROR: no data avaible between %s and %s' %(date1.strftime("%Y-%m-%d"),date2.strftime("%Y-%m-%d")))
    sys.exis(-1)

###########################################################################
# Download the data 
###########################################################################
print("Download the data:")

ftp_hadUK_Grid = FTP('ftp.ceda.ac.uk')
ftp_hadUK_Grid.encoding = "utf-8"
ftp_hadUK_Grid.login(user=options.username,passwd=options.password)
ftp_hadUK_Grid.cwd('badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/%s/%s/%s/%s/%s' %(version_grid,spt_res,variable,temp_res,update_version))

for filei in tqdm(list_of_files):
    print("\tDownload the file %s:" %(filei))
    if not os.path.exists(options.writedirectory+'/'+filei):
        with open(options.writedirectory+'/'+filei, 'wb') as fp:
            ftp_hadUK_Grid.retrbinary("RETR %s" % (filei), fp.write)
            print("\t\tcompleted.")
    else:
        print("\t\tthe file has been found.")

ftp_hadUK_Grid.quit()

###########################################################################
# Write the txt file if needed
###########################################################################
if options.mode == 'txt':
    if options.name == "":
        fout = open("%s/HadUK_Grid_%s_%s_%s.csv" %(options.outputdirectory,spt_res,variable,temp_res),'w')
    else:
        fout = open("%s/%s_HadUK_Grid_%s_%s_%s.csv" %(options.outputdirectory,options.name,spt_res,variable,temp_res),'w')

    fout.write('HadUK-Grid results\n')
    fout.write('\tVersion:\t%s\n' % (version_grid))
    fout.write('\tUpdate:\t%s\n' % (update_version))
    fout.write('\tSpatial Resolution:\t%s\n' % (spt_res))
    fout.write('\tTemporal Resolution:\t%s\n' % (temp_res))
    fout.write('\tVariable:\t%s\n' % (variable))
    if len(ROI) == 2:
        fout.write('\nFor the point (estimated by nearest distance)\tlat: %f\tlon: %f\n' % (ROI[0],ROI[1]))
        fout.write('\nDate;Value\n')
    elif len(ROI) == 4:
        fout.write('\nFor the ROI [S,N,W,E]: %f,%f,%f,%f\n' % (ROI[0],ROI[1],ROI[2],ROI[3]))
        fout.write('\nDate;Mean Value;Median Value;STD Value\n')

###########################################################################
# Read the data (and write the image)
###########################################################################
print("Read the data:")

for li in tqdm(list_of_files):
    print('\tFor %s' %(li))
    f = cf.read(options.writedirectory+'/'+li)[0]
    for fi in f:

        # Read the data
        data = fi.data.array
        lon = fi.constructs('longitude').value().array
        lat = fi.constructs('latitude').value().array

        # Read the date
        time = fi.constructs('time').value().array.flatten()
        atmos_epoch = datetime(1800, 1, 1, 0, 0, tzinfo=timezone.utc).timestamp()/3600 + time
        datedatai = datetime.fromtimestamp(atmos_epoch[0]*3600)

        if len(ROI) == 2:
            # print('\t\tAccording the options, we find the closest pixel to the given point...')
            disttmp = (lon.flatten()-ROI[1])**2 + (lat.flatten()-ROI[0])**2 
            idxdisttmp = np.argmin(disttmp)
            data = data.flatten()
            datapt = data[idxdisttmp]

            if date1 <= datedatai and date2 >= datedatai:
                fout.write('%s;%f\n' %(datedatai.strftime("%Y-%m-%dT%H:%M:%S"),datapt))

        elif len(ROI) == 4 and options.mode == 'txt':
            lonbbox = [ROI[2],ROI[3],ROI[3],ROI[2],ROI[2]]
            latbbox = [ROI[0],ROI[0],ROI[1],ROI[1],ROI[0]]

            # print('\t\tAccording the options, we compute the variable inside the given ROI...')
            path_pts = []
            for pti1 in range(len(lonbbox)):
                path_pts.append( (lonbbox[pti1],latbbox[pti1]))
            path_BBOX = path.Path(path_pts)
            areapts = np.vstack(((lon.flatten()),(lat.flatten()))).T
            mask_BBOX = path_BBOX.contains_points(areapts)
            idx = np.where(np.array(mask_BBOX)==True)[0]

            dataptmean = np.mean(data.flatten()[idx])
            dataptmedian = np.median(data.flatten()[idx])
            dataptstd = np.std(data.flatten()[idx])

            if date1 <= datedatai and date2 >= datedatai:
                fout.write('%s;%f;%f;%f\n' %(datedatai.strftime("%Y-%m-%dT%H:%M:%S"),dataptmean,dataptmedian,dataptstd))

fout.close()

###########################################################################
# Clean the work directory
###########################################################################
if options.clean == 'y':
    print('Clean the downloaded data, but keep the work directory')
    for li in tqdm(list_of_files):
        if os.path.exists(options.writedirectory+'/'+li):
            os.remove(options.writedirectory+'/'+li)

###########################################################################
# Create the quicklook figure
###########################################################################
if options.figure == 'y':
    print('Create the quicklook figure:')
    if options.name == "":
        df = pd.read_csv("%s/HadUK_Grid_%s_%s_%s.csv" %(options.outputdirectory,spt_res,variable,temp_res),skiprows=9,delimiter=';')
    else:
        df = pd.read_csv("%s/%s_HadUK_Grid_%s_%s_%s.csv" %(options.outputdirectory,options.name,spt_res,variable,temp_res),skiprows=9,delimiter=';')

    datefig = []
    for di in df['Date']:
        datefig.append(datetime.strptime(di, "%Y-%m-%dT%H:%M:%S"))

    if variable == 'rainfall':
        if len(ROI) == 2:
            plt.bar(datefig, df['Value'], label="Variable")
        elif len(ROI) == 4:
            plt.bar(datefig, df['Mean Value'], label="Mean Variable")
            plt.errorbar(datefig, df['Mean Value'],df['STD Value'], c="red", label="Mean/STD Values")
    else:
        plt.errorbar(datefig, df['Mean Value'],df['STD Value'], c="black", label='Mean and STD values')

    ax = plt.gca()
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(MonthLocator())
    ax.autoscale_view()
    plt.xlabel("Time")
    plt.ylabel("Variable Unit")
    plt.legend(loc='best')
if options.name == "":
    plt.title("%s/HadUK_Grid_%s_%s_%s" %(options.outputdirectory,spt_res,variable,temp_res))
    plt.savefig("%s/HadUK_Grid_%s_%s_%s.pdf" %(options.outputdirectory,spt_res,variable,temp_res), dpi=450)
else:
    plt.title("%s/%s_HadUK_Grid_%s_%s_%s" %(options.outputdirectory,options.name,spt_res,variable,temp_res))
    plt.savefig("%s/%s_HadUK_Grid_%s_%s_%s.pdf" %(options.outputdirectory,options.name,spt_res,variable,temp_res), dpi=450)

    print('Create the quicklook figure: OKAY')

###########################################################################
## END
###########################################################################
print('END OF THE PROCESSING')

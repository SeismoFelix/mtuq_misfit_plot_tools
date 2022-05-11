import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import math
import json
#My saviors today:
#https://stackoverflow.com/questions/30509890/how-to-plot-a-smooth-2d-color-plot-for-z-fx-y
#https://www.geeksforgeeks.org/read-json-file-using-python/
#https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-in-a-list
#https://towardsdatascience.com/read-netcdf-data-with-python-901f7ff61648
#https://stackoverflow.com/questions/2051744/reverse-y-axis-in-pyplot

def read_json(f_json):
    f = open(f_json)
    data = json.load(f)
    
    G=[data['rho'],data['v'],data['w'],data['kappa'],data['sigma'],data['h']]
    return(G)

def find_index(ds,G):
    par = ['rho','v','w','kappa','sigma','h']
    indexes = []
    for i in range(len(par)):
        indexes.append(np.where(ds[par[i]][:] == G[i])[0][0])

    print('indexes: Coordinates lowest misfit point:rho,v,w,kappa(strike),sigma(rake/slip),h(cos[dip])')
    print(indexes)
    print('Lowest misfit point:')
    print(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][indexes[3]][indexes[4]][indexes[5]][0])
    return(indexes)

def plot3d(x,y,z,name,axis,inv_ax):
    z = np.array(z)
    X, Y = np.meshgrid(x, y)
    Z = z.reshape(40,40)

    plt.pcolor(X, Y, Z)
    plt.xlabel(axis[0])
    plt.ylabel(axis[1])
    plt.title(axis[2])
    if inv_ax == 'x':
        plt.gca().invert_xaxis()
    elif inv_ax == 'y':
        plt.gca().invert_yaxis()
    plt.savefig(name)
    plt.close()
    #plt.show()

###Dip vs. Strike, best slip fixed
def dip_strike(ds,indexes):
    x_aux=ds['h'][:]
    x=[]
    for i in range(len(x_aux)):
        rad = math.acos(x_aux[i])
        x.append(math.degrees(rad))
    x=np.array(x)
    y=ds['kappa'][:]
    z=[]
    for i in range(len(x)):
        for j in range(len(y)):
            z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][indexes[4]][j][0])

    name='DipVsStrike_slip_fixed.pdf'
    axis = ['Dip','Strike','Slip = {}'.format(ds['sigma'][indexes[4]])]
    inv_ax = 'x'
    plot3d(x,y,z,name,axis,inv_ax)

####Slip vs. Strike, best dip fixed
def slip_strike(ds,indexes):
    x=ds['sigma'][:]
    y=ds['kappa'][:]
    z=[]
    for i in range(len(x)):
        for j in range(len(x)):
            z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][j][indexes[5]][0])

    axis = ['Slip','Strike','Dip = {}'.format(math.degrees(math.acos(ds['h'][indexes[5]])))]
    name='SlipVsStrike_dip_fixed.pdf'
    inv_ax = 'n'
    plot3d(x,y,z,name,axis,inv_ax)

####Slip vs. Dip, best strike fixed
def slip_dip(ds,indexes):
    x=ds['sigma'][:]
    y_aux=ds['h'][:]
    y=[]
    for i in range(len(y_aux)):
        rad = math.acos(y_aux[i])
        y.append(math.degrees(rad))
    y=np.array(y)
    z=[]

    for i in range(len(x)):
        for j in range(len(y)):
            z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][indexes[3]][j][i][0])
    name='SlipVsDip_strike_fixed.pdf'
    axis = ['Slip','Dip','Strike = {}'.format(ds['kappa'][indexes[3]])]
    inv_ax = 'y'
    plot3d(x,y,z,name,axis,inv_ax)

####Slip vs. Strike, best dip at each coordinate
def slip_strike_minmisfit(ds,indexes):
    x=ds['sigma'][:]
    y=ds['kappa'][:]
    z=[]
    for i in range(len(x)):
        for j in range(len(x)):
            z_aux = []
            for k in range(len(ds['h'][:])):
                z_aux.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][j][k][0])
            index_min = np.argmin(z_aux)
            z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][j][index_min][0])

    axis = ['Slip','Strike','Minimun mistif at each slip-strike par']
    name='SlipVsStrike_minimum_misfit.pdf'
    inv_ax = 'n'
    plot3d(x,y,z,name,axis,inv_ax)


f_netcdf = '20140826115645000DC_misfit.nc'
f_json = '20140826115645000DC_solution.json'
ds = nc.Dataset(f_netcdf)
G = read_json(f_json)
indexes = find_index(ds,G)

slip_strike_minmisfit(ds,indexes)
#dip_strike(ds,indexes)
#slip_strike(ds,indexes)
#slip_dip(ds,indexes)

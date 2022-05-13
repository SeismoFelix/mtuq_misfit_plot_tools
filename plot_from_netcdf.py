import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import math
import json
import sys
#My saviors today:
#https://stackoverflow.com/questions/30509890/how-to-plot-a-smooth-2d-color-plot-for-z-fx-y
#https://www.geeksforgeeks.org/read-json-file-using-python/
#https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-in-a-list
#https://towardsdatascience.com/read-netcdf-data-with-python-901f7ff61648
#https://stackoverflow.com/questions/2051744/reverse-y-axis-in-pyplot
#https://stackoverflow.com/questions/32461452/python-plot-3d-surface-with-colormap-as-4th-dimension-function-of-x-y-z
#https://jakevdp.github.io/PythonDataScienceHandbook/04.12-three-dimensional-plotting.html

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


def make_data_gmt(x,y,z,free_values,axis4d):
    ##http://gmt.soest.hawaii.edu/doc/5.3.2/supplements/meca/psmeca.html
    ##lon lat depth strike dip slip mag 0 0
    z=np.array(z)
    free_values = np.array(free_values)
    Z = z.reshape(len(x),len(y))
    FREE = free_values.reshape(len(x),len(y))
    
    c1 = x
    c2 = y
    c3 = '7.0'
    c7 = '4.6'
    
    open_file = open('psmeca_file_{}_{}_surface_{}.txt'.format(axis4d[0],axis4d[1],axis4d[2]),'w')
    header ='##lon lat depth strike dip slip mag 0 0\n'
    open_file.write(header)
    for i in range(len(x)):
        for j in range(len(y)):
            ##x=dip,y=strike,k=slip
            if axis4d[0] == 'dip' and axis4d[1] =='strike' and axis4d[2] == 'slip':
                c4 = y[j]
                c5 = x[i]
                c6 = FREE[i][j]
            ##x=slip,y=strike,free=dip
            elif axis4d[0] == 'slip' and axis4d[1] =='strike' and axis4d[2] == 'dip':
                c4 = y[j]
                c5 = FREE[i][j]
                c6 = x[i]
            ##i=slip,j=dip,k=strike
            elif axis4d[0] == 'slip' and axis4d[1] =='dip' and axis4d[2] == 'strike':
                c4 = FREE[i][j]
                c5 = y[j]
                c6 = x[i]
            line = '{} {} {} {} {} {} {} 0 0\n'.format(c1[i],c2[j],c3,c4,c5,c6,c7)
            open_file.write(line)
    open_file.close()
    
    open_file = open('color_misfit_{}_{}_surface_{}.txt'.format(axis4d[0],axis4d[1],axis4d[2]),'w')
    for i in range(len(x)):
        for j in range(len(y)):
            line = '{} {} {} {}\n'.format(x[i],y[j],Z[j][i],0.4)
            open_file.write(line)
    open_file.close()

    print(np.min(z))
    print(np.max(z))
                     
def plot3d(x,y,z,name,axis,inv_ax):
    z = np.array(z)
    X, Y = np.meshgrid(x, y)
    Z = z.reshape(len(x),len(y))

    plt.pcolor(X, Y, Z)
    plt.xlabel(axis[0])
    plt.ylabel(axis[1])
    plt.title(axis[2])
    if inv_ax == 'x':
        plt.gca().invert_xaxis()
    elif inv_ax == 'y':
        plt.gca().invert_yaxis()
    plt.colorbar(label="Misfit", orientation="horizontal")
    plt.gca().set_aspect('auto')
    plt.savefig(name)
    plt.close()
    #plt.show()

def plot4d(x,y,z,free_values,axis4d,name4d):
    
    c = np.array(z)
    C = c.reshape(len(x),len(y))
    zet = np.array(free_values)

    X,Y = np.meshgrid(x,y)
    Z = zet.reshape(len(x),len(y))

    fig = plt.figure()
    ax = fig.add_subplot(111,projection = '3d')

    scamap = plt.cm.ScalarMappable(cmap='viridis')
    fcolors = scamap.to_rgba(C)
    ax.plot_surface(X, Y, Z, facecolors=fcolors, cmap='inferno',shade=False)
    fig.colorbar(scamap,label="Misfit")
    
    ax.set_xlabel(axis4d[0])
    ax.set_ylabel(axis4d[1])
    ax.set_zlabel(axis4d[2])
    plt.title(axis4d[3])
    ax.view_init(45,330)
    plt.savefig(name4d)
    #ax.view_init(45,60)
    #ax.plot_surface(X, Y, Z,facecolors=cm.jet(C), shade=False)
    plt.show()

def h2d(h_values):
    dip=[]
    for i in range(len(h_values)):
        rad = math.acos(h_values[i])
        dip.append(math.degrees(rad))
    dip=np.array(dip)
    return(dip)

def make_figure_plane(ds,indexes,x_axis,y_axis,free):

    fault_dict = {
        'kappa': 'strike',
        'sigma': 'slip',
        'h': 'dip'
    }
    
    print('Making slice plot for plane x_axis:{}, y_axis:{} and {} fixed '.format(fault_dict[x_axis],fault_dict[y_axis],fault_dict[free]))

    if x_axis == 'h':
        x=h2d(ds[x_axis][:])
    else:
        x=ds[x_axis][:]
    if y_axis == 'h':
        y=h2d(ds[y_axis][:])
    else:
        y=ds[y_axis][:]
    
    z=[]

    for i in range(len(x)):
        for j in range(len(y)):
            if x_axis == 'h' and y_axis == 'kappa' and free == 'sigma':
                #i=dip,j=strike,k=slip
                z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][indexes[4]][j][0])
            elif x_axis == 'sigma' and y_axis == 'kappa' and free == 'h':
                #i=slip,j=strike,k=dip
                z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][j][indexes[5]][0])
            elif x_axis == 'sigma' and y_axis == 'h' and free == 'kappa':
                #i=slip,j=dip,k=strike
                z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][indexes[3]][j][i][0])
                
    if free == 'sigma':
        free_value = ds[free][indexes[4]]
    elif free == 'h':
        free_value = ds[free][indexes[5]]
        rad = math.acos(free_value)
        free_value = math.degrees(rad)
    elif free == 'kappa':
        free_value = ds[free][indexes[3]]

    name='{}_vs_{}_fixed_{}.pdf'.format(fault_dict[x_axis],fault_dict[y_axis],fault_dict[free])
    axis = [fault_dict[x_axis],fault_dict[y_axis],'{} = {} '.format(fault_dict[free],free_value)]

    if x_axis == 'h':
        inv_ax = 'x'
    elif y_axis == 'h':
        inv_ax = 'y'
    else:
        inv_ax ='n'

    plot3d(x,y,z,name,axis,inv_ax)

def make_figure_surface(ds,indexes,x_axis,y_axis,free):
    
    fault_dict = {
        'kappa': 'strike',
        'sigma': 'slip',
            'h': 'dip'
    }
    
    print('Making surface plot for x_axis:{}, y_axis:{} and  {} free'.format(fault_dict[x_axis],fault_dict[y_axis],fault_dict[free]))

    if x_axis == 'h':
        x=h2d(ds[x_axis][:])
    else:
        x=ds[x_axis][:]
    if y_axis == 'h':
        y=h2d(ds[y_axis][:])
    else:
        y=ds[y_axis][:]

    z=[]
    free_values = []

    for i in range(len(x)):
        for j in range(len(y)):
            z_aux = []
            for k in range(len(ds[free][:])):
                if x_axis == 'h' and y_axis == 'kappa' and free == 'sigma':
                    #i=dip,j=strike,k=slip
                    z_aux.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][k][j][0])
                elif x_axis == 'sigma' and y_axis == 'kappa' and free == 'h':
                    #i=slip,j=strike,k=dip
                    z_aux.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][j][k][0])
                elif x_axis == 'sigma' and y_axis == 'h' and free == 'kappa':
                    #i=slip,j=dip,k=strike
                    z_aux.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][k][j][i][0])
                else:
                    print('we have an issue with your axes {},{},{}'.format(x_axis,y_axis,free))
                    sys.exit()
                    
            index_min = np.argmin(z_aux)
            
            if free == 'h':
                free_value_aux = ds[free][index_min]
                rad = math.acos(free_value_aux)
                free_values.append(math.degrees(rad))
            else:
                free_values.append(ds[free][index_min])
            
            if x_axis == 'h' and y_axis == 'kappa' and free == 'sigma':
                z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][index_min][j][0])
            elif x_axis == 'sigma' and y_axis == 'kappa' and free == 'h':
                z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][i][j][index_min][0])
            elif x_axis == 'sigma' and y_axis == 'h' and free == 'kappa':
                z.append(ds['__xarray_dataarray_variable__'][indexes[0]][indexes[1]][indexes[2]][index_min][j][i][0])
                    
          
    axis = [fault_dict[x_axis],fault_dict[y_axis],'Minimun mistif at each {}-{} pair'.format(fault_dict[x_axis],fault_dict[y_axis])]
    axis4d = [fault_dict[x_axis],fault_dict[y_axis],fault_dict[free],'Minimun mistif surface at each {},{}, and {}'.format(fault_dict[x_axis],fault_dict[y_axis],fault_dict[free])]
    
    name='{}_vs_{}_minimum_misfit.pdf'.format(fault_dict[x_axis],fault_dict[y_axis])
    name4d ='{}_{}_{}_minimum_misfit_surface.pdf'.format(fault_dict[x_axis],fault_dict[y_axis],fault_dict[free])
    
    if x_axis == 'h':
        inv_ax = 'x'
    elif y_axis == 'h':
        inv_ax = 'y'
    else:
        inv_ax ='n'

    #plot3d(x,y,z,name,axis,inv_ax)
    #print('Making 4D plot')
    plot4d(x,y,z,free_values,axis4d,name4d)
    make_data_gmt(x,y,z,free_values,axis4d)

f_netcdf = '20140826115645000DC_misfit.nc'
f_json = '20140826115645000DC_solution.json'
ds = nc.Dataset(f_netcdf)
G = read_json(f_json)
indexes = find_index(ds,G)

#sigma : rake/slip
#kappa : strike
#h: cos(dip)
space=['sigma','kappa','h']

##FIGURES PLANES
##i=dip,j=strike,k=slip
#make_figure_plane(ds,indexes,space[2],space[1],space[0])
##x=slip,y=strike,free=dip
#make_figure_plane(ds,indexes,space[0],space[1],space[2])
##i=slip,j=dip,k=strike
#make_figure_plane(ds,indexes,space[0],space[2],space[1])

##FIGURES SURFACES
##x=dip,y=strike,k=slip
make_figure_surface(ds,indexes,space[2],space[1],space[0])
##x=slip,y=strike,free=dip
#make_figure_surface(ds,indexes,space[0],space[1],space[2])
##i=slip,j=dip,k=strike
#make_figure_surface(ds,indexes,space[0],space[2],space[1])

from tkinter.filedialog import askopenfilename
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import numpy as np
import sys,os
import math

print('select csv file containing extracted path features')
fdf = pd.read_csv(askopenfilename())

print('select csv file with behavior and stimulus timings')    
ktdf = pd.read_csv(askopenfilename())
ktdf = ktdf[ktdf['defensive strategy'] != 'mistrial']
ktdf = ktdf[ktdf['day'] == 1]
animals_to_include = ktdf[ktdf['exclusion rationale'].isnull()].animal.unique()

fdf = fdf[fdf['animal'].isin(animals_to_include)]
fdf = fdf[fdf['outcome'] == 'escape']

# within escape trials 
# ChR2 females follow straighter paths in the large shadow phase
# ChR2 males follow curvier paths in the small shadow phase

#fdf = fdf[fdf['sex'] == 'F']
fdf = fdf[fdf['sex'] == 'M']

sys.path.append(os.path.join(os.path.dirname(__file__),'src'))
from scientific import plot_scattermeans

fig = plt.figure(figsize=(9,4))
gs = GridSpec(2,5,figure=fig)

ax_scatC = fig.add_subplot( gs[0,0:2] )

ax_crv = fig.add_subplot( gs[0,2] )
ax_crvs = fig.add_subplot( gs[0,3] )            # path curvature for escapes initiated when shadow is small
ax_crvl = fig.add_subplot( gs[0,4] )

ax_scatS = fig.add_subplot( gs[1,0:2] )
ax_spd = fig.add_subplot( gs[1,2] )
ax_spds = fig.add_subplot( gs[1,3] )
ax_spdl = fig.add_subplot( gs[1,4] )

fdf_small = fdf[ (fdf['latency'] < 3.0 ) ]
fdf_large = fdf[ (fdf['latency'] > 3.0) ]

ax_scatC.scatter(fdf[ (fdf['phenotype'] == 'eYFP') ]['latency'],fdf[ (fdf['phenotype'] == 'eYFP') ]['curvature'],color='gold')
ax_scatC.scatter(fdf[ (fdf['phenotype'] == 'ChR2') ]['latency'],fdf[ (fdf['phenotype'] == 'ChR2') ]['curvature'],color='dodgerblue')

ax_scatS.scatter(fdf[ (fdf['phenotype'] == 'eYFP') ]['latency'],fdf[ (fdf['phenotype'] == 'eYFP') ]['speed-peak'],color='gold')
ax_scatS.scatter(fdf[ (fdf['phenotype'] == 'ChR2') ]['latency'],fdf[ (fdf['phenotype'] == 'ChR2') ]['speed-peak'],color='dodgerblue')

for ph in (2,4):
    ax_scatC.axvline(ph,linestyle='--',color='k')
    ax_scatS.axvline(ph,linestyle='--',color='k')

ax_scatC.set_ylabel('Curvature')
ax_scatS.set_ylabel('Peak Speed (m/s)')
ax_scatS.set_xlabel('Run initiation latency (s)')
ax_scatC.set_xlim(0,6)
ax_scatS.set_xlim(0,6)


gdf = fdf.groupby('phenotype',sort=True)
plot_scattermeans(gdf,'curvature',ax_crv,ylabel='Curvature',xlabels=['ChR2','eYFP'],colors = ['dodgerblue','gold'] , min = 1.0, max = 2.5)

gdf = fdf.groupby('phenotype',sort=True)
plot_scattermeans(gdf,'speed-peak',ax_spd,ylabel='Peak Speed (m/s)',xlabels=['ChR2','eYFP'],colors = ['dodgerblue','gold'] , min = 0.25, max = 2.0)



gdf = fdf_small.groupby('phenotype',sort=True)
plot_scattermeans(gdf,'curvature',ax_crvs,ylabel='Curvature',xlabels=['ChR2','eYFP'],colors = ['dodgerblue','gold'] , min = 1.0, max = 2.5)

gdf = fdf_large.groupby('phenotype',sort=True)
plot_scattermeans(gdf,'curvature',ax_crvl,ylabel='Curvature',xlabels=['ChR2','eYFP'],colors = ['dodgerblue','gold'] , min = 1.0, max = 2.5)

gdf = fdf_small.groupby('phenotype',sort=True)
plot_scattermeans(gdf,'speed-peak',ax_spds,ylabel='Peak Speed (m/s)',xlabels=['ChR2','eYFP'],colors = ['dodgerblue','gold'] , min = 0.25, max = 2.0)

gdf = fdf_large.groupby('phenotype',sort=True)
plot_scattermeans(gdf,'speed-peak',ax_spdl,ylabel='Peak Speed (m/s)',xlabels=['ChR2','eYFP'],colors = ['dodgerblue','gold'] , min = 0.25, max = 2.0)

for ax in (ax_scatC,ax_crvs,ax_crvl,ax_scatS,ax_spds,ax_spdl,ax_crv,ax_spd):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

fig.tight_layout()
#plt.savefig('figs/path-features-comparison.png',format='png')
plt.show()    
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

sys.path.append(os.path.join(os.path.dirname(__file__),'src'))
from scientific import plot_scattermeans

fig = plt.figure(figsize=(8,3))
gs = GridSpec(1,3,figure=fig)

ax_mc = fig.add_subplot( gs[0,0] )
ax_ms = fig.add_subplot( gs[0,1] )
ax_ma = fig.add_subplot( gs[0,2] )

fdf_m = fdf[ (fdf['sex'] == 'M') ]
fdf_f = fdf[ (fdf['sex'] == 'F') ]

gdf = fdf_m.groupby('phenotype',sort=True)
plot_scattermeans(gdf,'curvature',ax_mc,ylabel='Curvature',xlabels=['ChR2','eYFP'],colors = ['dodgerblue','gold'] , min = 0.75, max = 2.5)
plot_scattermeans(gdf,'speed-peak',ax_ms,ylabel='Peak Speed',xlabels=['ChR2','eYFP'],colors = ['dodgerblue','gold'] , min = 0.0, max = 1.75)
plot_scattermeans(gdf,'acc-peak',ax_ma,ylabel='Peak Acceleration',xlabels=['ChR2','eYFP'],colors = ['dodgerblue','gold'] , min = 0.0, max = 20.0)

for ax in (ax_mc,ax_ms,ax_ma):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

fig.tight_layout()
plt.savefig('figs/path-features-comparison.png',format='png')
plt.show()    
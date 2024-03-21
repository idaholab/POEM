import numpy as np
import pandas as pd
import os
from matplotlib import pyplot as plt
import matplotlib
matplotlib.rc('xtick', labelsize=12)
matplotlib.rc('ytick', labelsize=12)
matplotlib.rc('axes', labelsize=12)

path = "/Users/wangc//projects/POEM/workflow/sauq/sauq_runs/"
filename = os.path.abspath(os.path.join(path, 'stats_dump_0.csv'))

inps = ['damage']
vars = ['RL', 'NL', 'k']

df_stats = pd.read_csv(filename)

fig, ax = plt.subplots(figsize=(8,6))
for var in vars:
  for inp in inps:
    col = 'nsen_'+var+'_'+inp
    ax.plot(df_stats['irrT'], df_stats[col], label=var+"|"+inp)

ax.set_xlabel('Temperature')
ax.set_ylabel('Sensitivity')
plt.legend(title='Responses where:')
plt.show()

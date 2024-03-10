import matplotlib.pyplot as plt
import pandas as pd
import os, sys

cwd = os.getcwd()
sys.path.append(os.path.join(cwd, "..", "..", "..", "..", "src", "poem"))
from plotUtils import optPath, animatePlot

sys.path.append(os.path.join(cwd, "..", "..", "..", "models"))
from matyas import evaluate as matyas


# Load existing pre-trained data
extData = pd.read_csv('LHS_dump.csv', header=0)

# Load optimization data
data = {}
with open('opt_export_0.csv','r', encoding = "utf-8-sig") as infile:
  data = {'x':[],'y':[],'z':[],'a':[]}
  for l,line in enumerate(infile):
    line = line.strip().split(',')
    if l==0:
      ix = line.index('x')
      iy = line.index('y')
      # iz = line.index('z')
      ia = line.index('accepted')
      continue
    data['x'].append(float(line[ix]))
    data['y'].append(float(line[iy]))
    # data[case]['z'].append(float(line[iz]))
    data['a'].append(line[ia])

fig = plt.figure(figsize=(12,8))
optPath(data['x'], data['y'], data['a'], fig, 'matyas',matyas,None,(-10,10),(-10,10),log=False, xp=extData['x'], yp=extData['y'])
animatePlot(data['x'], data['y'], data['a'], fig, 'matyas',matyas,None,(-10,10),(-10,10),log=False, xp=extData['x'], yp=extData['y'])


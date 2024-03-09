import matplotlib.pyplot as plt
import os, sys

cwd = os.getcwd()
sys.path.append(os.path.join(cwd, "..", "..", "..", "..", "src", "poem"))
from plotUtils import optPath, animatePlot

sys.path.append(os.path.join(cwd, "..", "..", "..", "models"))
from mishraBirdConstrained import evaluate as mishra
from mishraBirdConstrained import constraint as mishra_c

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
optPath(data, fig, 'mishra',mishra,mishra_c,(-10,0),(-6.5,0),log=False)
animatePlot(data, fig, 'mishra',mishra,mishra_c,(-10,0),(-6.5,0),log=False)


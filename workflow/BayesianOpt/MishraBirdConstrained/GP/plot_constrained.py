# Copyright 2017 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
  Module for plotting the various 2d optimization functions included
  in this folder, particularly for obtaining plottable values. Mostly
  used for debugging processes.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.colors as colors
import pickle as pk
import sys, os

samps = 500

def plotFunction(title,method,constraint,xscale,yscale,cscale=None,log=True):
  """
    Plots a 2D function as a colormap.  Returns parameters suitable to plotting in a pcolormesh call.
    @ In, title, string, title name for figure
    @ In, method, function, method to call with x,y to get z result
    @ In, constraint, function, boolean method that determines acceptability
    @ In, xscale, tuple(float), low/hi value for x
    @ In, yscale, tuple(float), low/hi value for y
    @ In, cscale, tuple(float), optional, low and high values for the color map
    @ In, log, bool, optional, if False will not lognormalize the color map
    @ Out, X, np.array(np.array(float)), mesh grid of X values
    @ Out, Y, np.array(np.array(float)), mesh grid of Y values
    @ Out, Z, np.array(np.array(float)), mesh grid of Z (response) values
  """
  print('plotting',title)
  fig = plt.figure(title)
  ax = fig.add_subplot(111)#,projection='3d')
  xs = np.linspace(xscale[0],xscale[1],samps)
  ys = np.linspace(yscale[0],yscale[1],samps)
  X,Y = np.meshgrid(xs,ys)
  Z = method(X,Y)
  #Z[np.where(not constraint(X,Y))] = np.nan
  for i,x in enumerate(xs):
    for j,y in enumerate(ys):
      if constraint(x,y)<=0:
        Z[j][i] = np.nan
      #else:
      #  print(i,x,'|',j,y,'|',Z[i][j])
  Zm = np.ma.masked_where(np.isnan(Z),Z)
  print('min: {}, max:{}'.format(np.nanmin(Z),np.nanmax(Z)))
  if log:
    if cscale is None:
      vmin,vmax = np.nanmin(Z),np.nanmax(Z)
    else:
      vmin,vmax = cscale
    norm = colors.LogNorm(vmin=vmin,vmax=vmax)
  else:
    norm = colors.Normalize()
  ax.pcolormesh(X,Y,Zm)#,norm=norm)
  plt.title(title)
  return X,Y,Zm

cwd = os.getcwd()
sys.path.append(os.path.join(cwd, "..", "..", "..", "models"))
from mishraBirdConstrained import evaluate as mishra
from mishraBirdConstrained import constraint as mishra_c
x,y,z = plotFunction('Mishra Bird',mishra,mishra_c,(-10,0),(-6.5,0),log=False)
with open('mishra_plotdata.pk','wb') as file:
  pk.dump((x,y,z),file)

plt.show()

# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.lines import Line2D
import matplotlib.colors as colors
import numpy as np
import pickle as pk
from collections import defaultdict

markerMap = {'first': 'yo',
            'accepted': 'go',
            'rejected': 'rx',
            'pre-existing': 'c^',
            'final': 'mo'}
markers = defaultdict(lambda: 'k.', markerMap)

def addPoint(ax, x, y, accepted):
  lines = ax.plot(x, y, f'{markers[accepted]}')
  return lines

def plotFunction(fig, title,method,constraint,xscale,yscale,cscale=None,log=False, samps=500, xp=None, yp=None):
  """
    Plots a 2D function as a colormap.  Returns parameters suitable to plotting in a pcolormesh call.
    @ In, title, string, title name for figure
    @ In, method, function, method to call with x,y to get z result
    @ In, constraint, function, boolean method that determines acceptability
    @ In, xscale, tuple(float), low/hi value for x
    @ In, yscale, tuple(float), low/hi value for y
    @ In, cscale, tuple(float), optional, low and high values for the color map
    @ In, log, bool, optional, if False will not lognormalize the color map
    @ In, samps, int
    @ In, extData, pandas.Dataframe
    @ Out, X, np.array(np.array(float)), mesh grid of X values
    @ Out, Y, np.array(np.array(float)), mesh grid of Y values
    @ Out, Z, np.array(np.array(float)), mesh grid of Z (response) values
  """
  print('plotting',title)
  ax = fig.add_subplot(111)
  xs = np.linspace(xscale[0],xscale[1],samps)
  ys = np.linspace(yscale[0],yscale[1],samps)
  X,Y = np.meshgrid(xs,ys)
  Z = method(X,Y)
  #Z[np.where(not constraint(X,Y))] = np.nan
  # constraint function from optimization, Negative for violated constraint
  if constraint is not None:
    for i,x in enumerate(xs):
      for j,y in enumerate(ys):
        if constraint(x,y)<=0:
          Z[j][i] = np.nan
    Zm = np.ma.masked_where(np.isnan(Z),Z)
  else:
    Zm = Z
  print('min: {}, max:{}'.format(np.nanmin(Z),np.nanmax(Z)))
  if log:
    if cscale is None:
      vmin,vmax = np.nanmin(Z),np.nanmax(Z)
    else:
      vmin,vmax = cscale
    norm = colors.LogNorm(vmin=vmin,vmax=vmax)
  else:
    norm = colors.Normalize()
  if log:
    axPlot=ax.pcolormesh(X,Y,Zm,norm=norm)
  else:
    axPlot=ax.pcolormesh(X,Y,Zm)
  if xp is not None and yp is not None:
    ax.scatter(xp, yp, marker=markerMap['pre-existing'][1], c=markerMap['pre-existing'][0])
  fig.colorbar(axPlot, ax=ax)
  plt.title(title)
  with open(title+'.pk','wb') as file:
    pk.dump((X, Y, Zm),file)

  plt.savefig(title+'.png')
  return fig, ax

def animate(n, ax, x, y, a):
  mk = markers[a[n]]
  ax.plot(x[n], y[n], mk, markersize=10)
  return ax

def animatePlot(x, y, a, fig, title,method,constraint,xscale,yscale,cscale=None,log=False, samps=500, xp=None, yp=None):
  fig, ax = plotFunction(fig, title,method,constraint,xscale,yscale,cscale,log, samps, xp, yp)
  lns = []
  for cond in markerMap.keys():
    lns.append(Line2D([0], [0], color=markerMap[cond][0], marker=markerMap[cond][1]))
  fig.legend(lns, list(markerMap.keys()),
              loc='center right',
              borderaxespad=0.1,
              title='Legend')
  ani=animation.FuncAnimation(fig,animate,len(x), fargs=(ax, x, y, a), interval=5000000)
  Writer = animation.writers['ffmpeg']
  writer = Writer(fps=15,bitrate=1800)
  ani.save(title+'.mp4',writer=writer)

def optPath(x, y, a, fig, title,method,constraint,xscale,yscale,cscale=None,log=False, samps=500, xp=None, yp=None):
  fig, ax = plotFunction(fig, title,method,constraint,xscale,yscale,cscale,log, samps, xp, yp)
  for i in range(len(x)):
    mk = markers[a[i]]
    ax.plot(x[i], y[i], mk, markersize=10)

  lns = []
  for cond in markerMap.keys():
    lns.append(Line2D([0], [0], color=markerMap[cond][0], marker=markerMap[cond][1]))
  fig.legend(lns, list(markerMap.keys()),
              loc='center right',
              borderaxespad=0.1,
              title='Legend')
  plt.savefig(title+'_opt_path.png')

# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
#
# takes input parameters x,y
# returns value in "ans"
# constrained function
# optimal minimum at f(-3.1302468, -1.5821422) = -106.7645367
# parameter range is -10 <= x <= 0, -6.5 <= y <= 0
import numpy as np

def evaluate(x,y):
  """
    Evaluates Mishra bird function.
    @ In, x, float, value
    @ In, y, float, value
    @ Out, evaluate, value at x, y
  """
  evaluate = np.sin(y)*np.exp(1.-np.cos(x))**2 + np.cos(x)*np.exp(1.-np.sin(y))**2 + (x-y)**2
  return evaluate

def constraint(x,y):
  """
    Evaluates the constraint function @ a given point (x,y)
    @ In, x, float, value of the design variable x
    @ In, y, float, value of the design variable y
    @ Out, g(x,y), float, $g(x, y) = 25 - ((x+5.)**2 + (y+5.)**2)$
            the way the constraint is designed is that
            the constraint function has to be >= 0,
            so if:
            1) f(x,y) >= 0 then g = f
            2) f(x,y) >= a then g = f - a
            3) f(x,y) <= b then g = b - f
            4) f(x,y)  = c then g = 0.001 - (f(x,y) - c)
  """
  condition = 25.
  g = condition - ((x+5.)**2 + (y+5.)**2)
  return g

###
# RAVEN hooks
###

def run(self,Inputs):
  """
    RAVEN API
    @ In, self, object, RAVEN container
    @ In, Inputs, dict, additional inputs
    @ Out, None
  """
  self.z = evaluate(self.x,self.y)

def constrain(self):
  """
    Constrain calls the constraint function.
    @ In, self, object, RAVEN container
    @ Out, explicitConstrain, float, positive if the constraint is satisfied
           and negative if violated.
  """
  explicitConstrain = constraint(self.x,self.y)
  return explicitConstrain

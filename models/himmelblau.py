# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

def evaluate(x,y):
  """
    Evaluates Matya's function.
    @ In, x, float, value
    @ In, y, float, value
    @ Out, evaluate, float, value at x, y
  """
  return (x**2+y-11)**2 + (x+y**2-7)**2

def run(self,Inputs):
  """
    RAVEN API
    @ In, self, object, RAVEN container
    @ In, Inputs, dict, additional inputs
    @ Out, None
  """
  self.z2 = evaluate(self.x,self.y)

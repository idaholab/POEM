# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
#
# takes input parameters x,y
# returns value in "ans"
# optimal minimum at f(0,0) = 0
# parameter range is -10 <= x,y <= 10

def evaluate(x,y):
  """
    Evaluates Matya's function.
    @ In, x, float, value
    @ In, y, float, value
    @ Out, evaluate, float, value at x, y
  """
  return 0.26*((x**2) + (y**2)) - 0.48*x*y

def run(self,Inputs):
  """
    RAVEN API
    @ In, self, object, RAVEN container
    @ In, Inputs, dict, additional inputs
    @ Out, None
  """
  self.z1 = evaluate(self.x,self.y)

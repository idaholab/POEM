# from https://en.wikipedia.org/wiki/Test_functions_for_optimization
#
# takes input parameters x,y
# returns value in "ans"
# optimal minimum at f(3,2) = 0, f(-2.805118, 3.131312) = 0
# f(-3.779310, -3.283186) = 0, f(3.584428, -3.283186) = 0
# parameter range is -5 <= x,y <= 5

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

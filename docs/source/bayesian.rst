
.. _bayopt:

Bayesian Optimization
=====================
Bayesian optimization for optimal experimental design.

Example
^^^^^^^

In this analysis, set ``<AnalysisType>bayesian_optimization</AnalysisType>``.
The existing experiment data can be provided through ``<data>`` in ``<GlobalSettings>``.
For example:

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation verbosity="debug">
    <RunInfo>
      <WorkingDir>Optimization</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>bayesian_optimization</AnalysisType>
      <data>../LHS_mishra/sampling_dump.csv</data>
      <limit>10</limit>
      <Inputs>x, y</Inputs>
      <Outputs>z</Outputs>
    </GlobalSettings>

    <Distributions>
      <Uniform name='x'>
        <lowerBound>-10</lowerBound>
        <upperBound>0</upperBound>
      </Uniform>
      <Uniform name='y'>
        <lowerBound>-6.5</lowerBound>
        <upperBound>0</upperBound>
      </Uniform>
    </Distributions>

    <Models>
      <ExternalModel ModuleToLoad="../../models/mishraBirdConstrained.py" name="mishra" subType="">
        <inputs>x, y</inputs>
        <outputs>z</outputs>
      </ExternalModel>

    </Models>

    <Functions>
      <External file="../../models/mishraBirdConstrained.py" name="constraint1">
        <variables>x,y</variables>
      </External>
    </Functions>

  </Simulation>


Python External Model and Constrain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

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


# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import scipy.stats as st
import numpy as np

def initialize(self, runInfoDict, inputFiles):
  """
    Method to generate the observed data
    Assume alpha = 1.0, beta = 2.5, sigma = 1.0.
    and zout = alpha + beta * random + random * sigma
    @ In, runInfoDict, dict, the dictionary containing the runInfo
    @ In, inputFiles, list, the list of input files
    @ Out, None
  """
  # np.random.seed(1086)
  self.sigma = 1.0
  self.rand = np.random.randn()

def run(self, inputDict):
  """
    Method required by RAVEN to run this as an external model.
    log likelihood function
    @ In, self, object, object to store members on
    @ In, inputDict, dict, dictionary containing inputs from RAVEN
    @ Out, None
  """
  self.alpha = inputDict['alpha']
  self.beta = inputDict['beta']
  mu = self.alpha + self.beta * self.rand
  self.zout = mu + self.sigma * np.random.randn()
  #print(self.zout)

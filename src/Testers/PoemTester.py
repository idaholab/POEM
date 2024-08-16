# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
"""
Tests by running an executable.
"""
import os
import sys

POEM_LOC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')) # POEM Plugin Folder
sys.path.append(POEM_LOC)
import POEM.src._utils as POEM_utils

# get RAVEN base testers
RAVEN_FRAMEWORK_LOC = POEM_utils.getRavenLoc()
TESTER_LOC = os.path.join(RAVEN_FRAMEWORK_LOC, 'scripts', 'TestHarness', 'testers')
sys.path.append(TESTER_LOC)
from RavenFramework import RavenFramework as RavenTester

class PoemRun(RavenTester):
  """
    A POEM stand-alone test interface.
  """

  @staticmethod
  def get_valid_params():
    """
      Return a list of valid parameters and their descriptions for this type
      of test.
      @ In, None
      @ Out, params, _ValidParameters, the parameters for this class.
    """
    params = RavenTester.get_valid_params()
    params.add_param('inputArg', '-i', 'Input argument to POEM')
    # params.add_param('output', '-o', 'Output argument to POEM')
    params.add_param('norun', '-nr', 'Argument "norun" to POEM')
    return params

  def __init__(self, name, param):
    """
      Constructor.
      @ In, name, str, name of test
      @ In, params, dict, test parameters
      @ Out, None
    """
    RavenTester.__init__(self, name, param)
    self.peom_driver = os.path.join(POEM_LOC, 'POEM', 'src', 'peom.py')

  def get_command(self):
    """
      Return the command this test will run.
      @ In, None
      @ Out, cmd, string, command to run
    """
    cmd = ''
    pythonCmd = self._get_python_command()
    cmd = pythonCmd + " " + self.peom_driver + " " + self.specs["inputArg"] + " " + self.specs["input"]
    if self.specs['norun']:
      cmd = cmd + " " + self.specs['norun']

    return cmd

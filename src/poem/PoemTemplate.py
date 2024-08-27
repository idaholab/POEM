# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
"""
Created on April 1, 2024
@author: wangc

This module inherits from base Template class for Input Templates, which use an established input
template as an accelerated way to write new RAVEN workflows.
"""
import logging
import sys

import POEM.src._utils as POEM_utils
RAVEN_FRAMEWORK_LOC = POEM_utils.get_raven_loc()
sys.path.append(RAVEN_FRAMEWORK_LOC)

from ravenframework.InputTemplates.TemplateBaseClass import Template as TemplateBase
from ravenframework.utils import xmlUtils

logger = logging.getLogger(__name__)

class PoemTemplate(TemplateBase):
  """ POEM: Template Class """

  ###############
  # API METHODS #
  ###############
  def __init__(self):
    """
      Constructor.
      @ In, None
      @ Out, None
    """
    TemplateBase.__init__(self)
    self._validEntities = ['RunInfo', 'Files', 'Models', 'Distributions', 'Samplers', 'Optimizers', 'DataObjects', 'OutStreams', 'Functions', 'Steps', 'Metrics', 'VariableGroups']

  def loadTemplate(self, filename):
    """
      Loads template file statefully.
      @ In, filename, str, name of file to load (xml)
      @ Out, None
    """
    self._template, _ = xmlUtils.loadToTree(filename)

  def createWorkflow(self, inputs, miscDict):
    """
      creates a new RAVEN workflow based on the information in dicitonary "inputs".
      @ In, inputs, dict, dictionary that contains xml node info that need to append, i.e. {RavenXMLNodeTag: ListOfNodes}
      @ In, miscDict, dict, dictionary that contains xml node text info that need to update, i.e. {RavenXMLNodeTag: value}
      @ Out, xml.etree.ElementTree.Element, modified copy of template ready to run
    """
    # call the base class to read in the template; this just creates a copy of the XML tree in self._template.
    template = TemplateBase.createWorkflow(self)
    runInfo = template.find('RunInfo')

    for key, val in inputs.items():
      if len(list(template.iter(key))) != 0:
        if key == 'RunInfo':
          for subnode in val:
            sub = runInfo.find(subnode.tag)
            if sub is not None:
              sub.text = subnode.text
            else:
              runInfo.append(subnode)
        else:
          for subnode in template.iter(key):
            if len(val) > 0:
              subnode.extend(val)
          # Update Models info
          if key == 'Models':
            for multiRunNode in template.iter('MultiRun'):
              modelNode = multiRunNode.find('Model')
              if modelNode.get('type') not in ['ROM', 'EnsembleModel']:
                modelNode.text = val[0].get('name')
                modelNode.attrib['type'] = val[0].tag
              # remove 'dummyIN' Dataobject Input when there is a code
              if val[0].tag == 'Code':
                inputNodes = multiRunNode.findall('Input')
                for inp in inputNodes:
                  if inp.text.lower() == 'dummyin' and inp.get('class') == 'DataObjects':
                    multiRunNode.remove(inp)
            for subnode in template.iter(key):
              ensemble = subnode.find('EnsembleModel')
              if ensemble:
                for m in ensemble.iter('Model'):
                  if m.text.strip().lower() == 'model':
                    m.text = val[0].get('name')
                    m.attrib['type'] = val[0].tag
      else:
        extraNode = xmlUtils.newNode(tag=key)
        extraNode.extend(val)
        template.append(extraNode)

    for key, val in miscDict.items():
      for subnode in template.iter(key):
        if val:
          subnode.text = val
    return template

  def writeWorkflow(self, template, destination, run=False):
    """
      Writes a template to file.
      @ In, template, xml.etree.ElementTree.Element, file to write
      @ In, destination, str, path and filename to write to
      @ In, run, bool, optional, if True then run the workflow after writing? good idea?
      @ Out, errors, int, 0 if successfully wrote [and run] and nonzero if there was a problem
    """
    TemplateBase.writeWorkflow(self, template, destination, run)

  def runWorkflow(self, destination):
    """
      Runs the workflow at the destination.
      @ In, destination, str, path and filename of RAVEN input file
      @ Out, res, int, system results of running the code
    """
    TemplateBase.runWorkflow(self, destination)

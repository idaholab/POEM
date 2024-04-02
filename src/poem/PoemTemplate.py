"""
Created on April 1, 2024
@author: wangc

This module inherits from base Template class for Input Templates, which use an established input
template as an accelerated way to write new RAVEN workflows.
"""
import logging

from ravenframework.InputTemplates.TemplateBaseClass import Template as TemplateBase

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

  def loadTemplate(self, filename, path):
    """
      Loads template file statefully.
      @ In, filename, str, name of file to load (xml)
      @ In, path, str, path (maybe relative) to file
      @ Out, None
    """
    TemplateBase.loadTemplate(self, filename, path)

  def createWorkflow(self, inputs, miscDict):
    """
      creates a new RAVEN workflow based on the information in dicitonary "inputs".
      @ In, inputs, dict, dictionary that contains xml node info that need to append, i.e. {RavenXMLNodeTag: ListOfNodes}
      @ In, miscDict, dict, dictionary that contains xml node text info that need to update, i.e. {RavenXMLNodeTag: value}
      @ Out, xml.etree.ElementTree.Element, modified copy of template ready to run
    """
    # call the base class to read in the template; this just creates a copy of the XML tree in self._template.
    template = TemplateBase.createWorkflow(self)
    for key, val in inputs.items():
      for subnode in template.iter(key):
        if val:
          subnode.extend(val)
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

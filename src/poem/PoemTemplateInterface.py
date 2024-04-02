"""
Created on April 1, 2024
@author: wangc

This module is the POEM Template interface, which use the user provided input XML
file to construct the corresponding RAVEN workflows i.e. RAVEN input XML file.
"""
import os
import sys
import copy
import logging
import argparse
import numpy as np
import xml.etree.ElementTree as ET

logging.basicConfig(format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
# To enable the logging to both file and console, the logger for the main should be the root,
# otherwise, a function to add the file handler and stream handler need to be created and called by each module.
# logger = logging.getLogger(__name__)
logger = logging.getLogger()
# # create file handler which logs debug messages
fh = logging.FileHandler(filename='poem.log', mode='w')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

try:
  from ._utils import get_raven_loc
  logger.info('Import "get_raven_loc" from "_utils"')
except ImportError:
  logger.info('Import "get_raven_loc" from "POEM.src._utils"')
  from POEM.src.poem._utils import get_raven_loc

## We need to add raven to the system path, since this file will be executed before RAVEN
## Otherwise, an ModuleNotFoundError will be raised to complain no module named 'ravenframework'
ravenFrameworkPath = get_raven_loc()
sys.path.append(os.path.join(ravenFrameworkPath, '..'))

from ravenframework.utils import xmlUtils
try:
  logger.info('Import modules from "PoemTemplate" and "poemUtils"')
  from .PoemTemplate import PoemTemplate
  from . import poemUtils
except ImportError:
  logger.info('Import modules from "POEM.src.poem.PoemTemplate" and "POEM.src.poem.poemUtils"')
  from POEM.src.poem.PoemTemplate import PoemTemplate
  from POEM.src.poem import poemUtils

class PoemTemplateInterface(object):
  """
    POEM Template Interface
  """
  # distribution template
  uniformDistNode = xmlUtils.newNode('Uniform')
  uniformDistNode.append(xmlUtils.newNode('lowerBound'))
  uniformDistNode.append(xmlUtils.newNode('upperBound'))
  # sampled variables template
  samplerVarNode = xmlUtils.newNode('variable')
  samplerVarNode.append(xmlUtils.newNode('distribution'))
  # External Model template
  externalModelNode = xmlUtils.newNode(tag='ExternalModel', attrib={'name':None, 'subType':None, 'ModuleToLoad':None})
  externalModelNode.append(xmlUtils.newNode('inputs'))
  externalModelNode.append(xmlUtils.newNode('outputs'))
  # BayCal.LikelihoodModel External Model template
  lhExternalModelNode = xmlUtils.newNode(tag='ExternalModel', attrib={'name':None, 'subType':'BayCal.LikelihoodModel'})
  lhExternalModelNode.append(xmlUtils.newNode('inputs'))
  lhExternalModelNode.append(xmlUtils.newNode('outputs'))
  lhModelNode = xmlUtils.newNode(tag='LikelihoodModel', attrib={'type':'normal'})
  lhModelNode.append(xmlUtils.newNode('simTargets'))
  lhModelNode.append(xmlUtils.newNode(tag='expTargets', attrib={'shape':None, 'computeCov':None, 'correlation':None}))
  lhModelNode.append(xmlUtils.newNode(tag='biasTargets'))
  lhModelNode.append(xmlUtils.newNode(tag='expCov', attrib={'diag':True}))
  lhModelNode.append(xmlUtils.newNode(tag='biasCov', attrib={'diag':True}))
  lhModelNode.append(xmlUtils.newNode(tag='romCov', attrib={'diag':True}))
  reductionNode = xmlUtils.newNode(tag='reduction')
  reductionNode.append(xmlUtils.newNode(tag='type'))
  reductionNode.append(xmlUtils.newNode(tag='truncationRank'))
  basisNode = xmlUtils.newNode(tag='basis', attrib={'shape':None})
  lhModelNode.append(reductionNode)
  lhModelNode.append(basisNode)
  lhExternalModelNode.append(lhModelNode)


  def __init__(self, filename):
    """
      Constructor.
      @ In, filename, the filename of POEM input
      @ Out, None
    """
    self._inputRoot, _ = xmlUtils.loadToTree(filename) # store the root of ET tree of POEM input
    self._inputVarList = [] # user provided input variable list
    self._externalModelList = []
    self._externalModelInputDict = {} # dictionary stores the inputs for each external model i.e. {externalModelName: list of inputs}
    self._externalModelOutputDict = {} # dictionary stores the outputs for each external model i.e. {externalModelName: list of outputs}
    self._distList = [] # list of constructed Distributions (ET element)
    self._sampVarList = [] # list of constructed sampled variables (ET element)
    self._ensembleModelList = [] # list of constructed models that are connected by EnsembleModel (ET element)
    self._dsList = [] # list of constructed data objects that are used for EnsembleModel (ET element)
    self._printList = [] # list of constructed output streams (ET element)
    self._variableGroupsList = [] # list of constructed variable groups (ET element)
    self._inputDict = {} # dictionary stores the user provided information, constructed from self._miscDict
    self._miscDict =  {'WorkingDir':'.',
                       'limit':'20'} # dictionary stores some default values and required inputs

  def getOutput(self):
    """
      get the processed outputs from this class: PoemTemplateInterface
      @ In, None
      @ Out, (outputDict, miscDict), tuple, first dictionary contains the whole element that need to be appended in
        the templated input, while the second dictionary contains only the values that need to be replaced.
    """
    outputDict = {'Models': self._externalModelList,
                  'EnsembleModel': self._ensembleModelList,
                  'MonteCarlo': self._sampVarList,
                  'Distributions': self._distList,
                  'DataObjects': self._dsList,
                  'OutStreams': self._printList,
                  'Simulations': self._variableGroupsList}
    miscDict = {'WorkingDir': self._inputDict['WorkingDir'],
                'limit': self._inputDict['limit']}
    return outputDict, miscDict

  def readInput(self):
    """
      Read the POEM input files, and construct corresponding ET elements
      @ In, None
      @ Out, None
    """
    logger.info("Start to process input file with root node: %s", self._inputRoot.tag)
    # process GlobalSettings
    globalSettingsNode = self.findRequiredNode(self._inputRoot, 'GlobalSettings')
    self.readGlobalSettings(globalSettingsNode)
    # process Variables
    variablesNode = self.findRequiredNode(self._inputRoot, 'Variables')
    self.readVariables(variablesNode)

    self.checkInput()
    # build external model
    externalModel = copy.deepcopy(self._externalModelList)
    self.buildExternalModel(externalModel)
    self.buildModelListForEnsembleModel()

  def readGlobalSettings(self, xmlNode):
    """
      Read the GlobalSettings XML node from the input root
      @ In, xmlNode, xml.etree.ElementTree.Element, the input root xml
      @ Out, None
    """
    logger.info("Start to read 'GlobalSettings' node")
    for key, val in self._miscDict.items():
      if val == 'required':
        node = self.findRequiredNode(xmlNode, key)
        self._inputDict[key] = copy.deepcopy(node)
      else:
        node = xmlNode.find(key)
        if node is not None:
          self._inputDict[key] = node.text

  def readVariables(self, xmlNode):
    """
      Read the Variables XML node from the input XML
      @ In, xmlNode, xml.etree.ElementTree.Element, the input XML node
      @ Out, None
    """
    logger.info("Start to read 'Variables' node")
    for node in xmlNode:
      self.readSingleVariable(node)

  def readSingleVariable(self, xmlNode):
    """
      Read the single Variable XML node from the input XML
      @ In, xmlNode, xml.etree.ElementTree.Element, the input XML node
      @ Out, None
    """
    logger.debug("Start to read single variable: %s", xmlNode.tag)
    varName = xmlNode.tag
    self._inputVarList.append(varName)
    distName = varName + '_dist'
    dist = self.findRequiredNode(xmlNode, 'Uniform')
    bounds = poemUtils.convertNodeTextToFloatList(dist.text)
    if bounds[0] >= bounds[1]:
      logger.warning('Provided lower bound exceeds the upper bound of uniform distribution of variable %s', varName)
      logger.warning('Swap the bounds of uniform distribution of variable %s', varName)
    lower, upper = min(bounds), max(bounds)
    distNode = copy.deepcopy(self.uniformDistNode)
    distNode.attrib['name'] = distName
    distNode.find('lowerBound').text = str(lower)
    distNode.find('upperBound').text = str(upper)
    # variable node for Samplers
    sampNode = copy.deepcopy(self.samplerVarNode)
    sampNode.attrib['name'] = varName
    sampNode.find('distribution').text = distName
    self._distList.append(distNode)
    self._sampVarList.append(sampNode)
    logger.debug("End reading single variable: %s", xmlNode.tag)


  def checkInput(self):
    """
      Check the consistency of user provided inputs
      @ In, None
      @ Out, None
    """
    logger.info("Checking the consistency of user provided input")


  def buildExternalModel(self, templateModel):
    """
      Build the LOGOS.CapitalInvestmentModel based on the POEM input
      @ In, templateModel, xml.etree.ElementTree.Element, templated LOGOS.CapitalInvestmentModel
      @ Out, None
    """
    modelName = 'ToBeDetermined'
    templateModel.attrib['name'] = modelName
    variablesNode = self.findRequiredNode(templateModel, 'variables')
    varList = []


  def buildModelListForEnsembleModel(self):
    """
      Build list of models for RAVEN EnsembleModel based on the POEM input
      @ In, None
      @ Out, None
    """
    totalOutput = []
    for model in self._externalModelList:
      key = model.attrib['name']
      inputDS = 'input_' + key
      outputDS = 'output_' + key
      # build ensemble model list
      ensembleModelNode = self.buildModelForEnsembleModel(key, inputDS, outputDS)
      self._ensembleModelList.append(ensembleModelNode)
      # build corresponding data object list
      inputVars = ','.join(self._externalModelInputDict[key])
      pointSet = self.buildPointSet(inputDS, inputVars, 'OutputPlaceHolder')
      self._dsList.append(pointSet)
      outputVars = ','.join(self._externalModelOutputDict[key])
      totalOutput.extend(self._externalModelOutputDict[key])
      pointSet = self.buildPointSet(outputDS, inputVars, outputVars)
      self._dsList.append(pointSet)
    # build main point set for whole ensemble model
    inputVars = ','.join(self._inputVarList)
    outputVars = ','.join(totalOutput)
    outputDS = "main_ps"
    pointSet = self.buildPointSet(outputDS, inputVars, outputVars)
    self._dsList.append(pointSet)

  @staticmethod
  def buildModelForEnsembleModel(modelName, inputDS, outputDS):
    """
      Build single model that used by EnsembleModel
      @ In, modelName, str, the name of model used as tag in xml.etree.ElementTree.Element
      @ In, inputDS, str, the name of input data object
      @ In, outputDS, str, the name of output data object
      @ Out, ensembleModelNode, xml.etree.ElementTree.Element, the ET element of Models under EnsembleModel
    """
    # ensemble model model node
    attribDict = {'class':'Models', 'type':'ExternalModel'}
    ensembleModelNode = xmlUtils.newNode(tag='Model', text=modelName, attrib=attribDict)
    attribDict = {'class':'DataObjects', 'type':'PointSet'}
    ensembleModelNode.append(xmlUtils.newNode(tag='Input', text=inputDS, attrib=attribDict))
    ensembleModelNode.append(xmlUtils.newNode(tag='TargetEvaluation', text=outputDS, attrib=attribDict))
    return ensembleModelNode

  @staticmethod
  def buildPointSet(name, inputs, outputs):
    """
      Build single PointSet XML node
      @ In, name, str, the name for the PointSet
      @ In, inputs, str, string that contains the list of input variables
      @ In, outputs, str, string that contains the list of output variables
      @ out, pointSet, xml.etree.ElementTree.Element, the constructed PointSet XML node
    """
    pointSet = xmlUtils.newNode(tag='PointSet', attrib={'name':name})
    pointSet.append(xmlUtils.newNode(tag='Input', text=inputs))
    pointSet.append(xmlUtils.newNode(tag='Output', text=outputs))
    return pointSet

  @staticmethod
  def findRequiredNode(xmlNode, nodeTag):
    """
      Find the required xml node
      @ In, xmlNode, xml.etree.ElementTree.Element, xml element node
      @ In, nodeTag, str, node tag that is used to find the node
      @ Out, subnode, xml.etree.ElementTree.Element, xml element node
    """
    subnode = xmlNode.find(nodeTag)
    if subnode is None:
      raise IOError('Required node ' + nodeTag + ' is not found in the input file!')
    return subnode

if __name__ == '__main__':
  logger.info('Welcome to the POEM Templated RAVEN Runner!')
  parser = argparse.ArgumentParser(description='POEM Templated RAVEN Runner')
  parser.add_argument('-i', '--input', nargs=1, required=True, help='POEM input filename')
  parser.add_argument('-t', '--template', nargs=1, required=True, help='POEM template filename')
  parser.add_argument('-o', '--output', nargs=1, help='POEM output filename')

  args = parser.parse_args()
  args = vars(args)
  inFile = args['input'][0]
  logger.info('POEM input file: %s', inFile)
  tempFile = args['template'][0]
  logger.info('POEM template file: %s', tempFile)
  if args['output'] is not None:
    outFile = args['output'][0]
    logger.info('POEM output file: %s', outFile)
  else:
    outFile = 'raven_' + inFile.strip()
    logger.warning('Output file is not specifies, default output file with name ' + outFile + ' will be used')

  # read capital budgeting input file
  templateInterface = PoemTemplateInterface(inFile)
  templateInterface.readInput()
  outputDict, miscDict = templateInterface.getOutput()

  # create template class instance
  templateClass = PoemTemplate()
  # load template
  here = os.path.abspath(os.path.dirname(tempFile))
  logger.info(' ... working directory: %s', here)
  tempFile = os.path.split(tempFile)[-1]
  templateClass.loadTemplate(tempFile, here)
  logger.info(' ... workflow successfully loaded ...')
  # create modified template
  template = templateClass.createWorkflow(outputDict, miscDict)
  logger.info(' ... workflow successfully modified ...')
  # write files
  here = os.path.abspath(os.path.dirname(inFile))
  templateClass.writeWorkflow(template, os.path.join(here, outFile), run=False)
  logger.info('')
  logger.info(' ... workflow successfully created and run ...')
  logger.info(' ... Complete!')

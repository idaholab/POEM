# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
"""
Created on April 1, 2024
@author: wangc

This module is the POEM Template interface, which use the user provided input XML
file to construct the corresponding RAVEN workflows i.e. RAVEN input XML file.
"""
import os
import sys
import logging
from .templates import templateConfig
from . import poemUtils

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
  from ravenframework.utils import xmlUtils
except ImportError:
  try:
    from .._utils import get_raven_loc
    # from ._utils import get_raven_loc
    logger.info('Import "get_raven_loc" from "_utils"')
  except ImportError:
    logger.info('Import "get_raven_loc" from "POEM.src._utils"')
    from POEM.src._utils import get_raven_loc

  ## We need to add raven to the system path, since this file will be executed before RAVEN
  ## Otherwise, an ModuleNotFoundError will be raised to complain no module named 'ravenframework'
  ravenFrameworkPath = get_raven_loc()
  sys.path.append(os.path.join(ravenFrameworkPath, '..'))
  from ravenframework.utils import xmlUtils

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

  validAnalysis = ['sensitivity', 'sparse_grid_construction', 'sparse_grid_rom', 'lhs', 'mc', 'train_rom', 'bayesian_optimization', 'model_calibration']

  analysisRequired ={'sensitivity':['RunInfo', 'Files', 'Models', 'Distributions'],
                     'sparse_grid_construction':['RunInfo', 'Files', 'Models', 'Distributions'],
                     'sparse_grid_rom':['RunInfo', 'Files', 'Models', 'Distributions'],
                     'lhs':['RunInfo', 'Files', 'Distributions'],
                     'mc':['RunInfo', 'Files', 'Distributions'],
                     'train_rom':['RunInfo', 'Distributions'],
                     'bayesian_optimization':['RunInfo', 'Files', 'Models', 'Distributions'],
                     'model_calibration':['RunInfo', 'Files', 'Models', 'Distributions', 'LikelihoodModel']}

  analysisOptions ={'sensitivity':[],
                    'sparse_grid_construction':[],
                    'sparse_grid_rom':[],
                    'lhs':['Models'],
                    'mc':['Models'],
                    'train_rom':[],
                    'bayesian_optimization':['Functions'],
                    'model_calibration':[]}


  def __init__(self, filename):
    """
      Constructor.
      @ In, filename, the filename of POEM input
      @ Out, None
    """
    self._inputFile = filename
    self._inputRoot, _ = xmlUtils.loadToTree(filename) # store the root of ET tree of POEM input
    self._filenameRoot = os.path.split(filename)[-1]
    self._inputVarList = [] # user provided input variable list
    self._outputVarList = []
    self._externalModelList = []
    self._externalModelInputDict = {} # dictionary stores the inputs for each external model i.e. {externalModelName: list of inputs}
    self._externalModelOutputDict = {} # dictionary stores the outputs for each external model i.e. {externalModelName: list of outputs}
    self._distList = [] # list of constructed Distributions (ET element)
    self._samplerList = [] # list of constructed sampled variables (ET element)
    self._ensembleModelList = [] # list of constructed models that are connected by EnsembleModel (ET element)
    self._dsList = [] # list of constructed data objects that are used for EnsembleModel (ET element)
    self._printList = [] # list of constructed output streams (ET element)
    self._variableGroupsList = [] # list of constructed variable groups (ET element)
    self._inputDict = {} # dictionary stores the user provided information, constructed from self._miscDict
    self._pivot = 'time'
    self._limit = 1000
    self._initSamples = 20
    self._templateFile = None
    self._analysisType = None
    self._ravenNodeDict = {}
    self._statsPrefix = ['skewness', 'variationCoefficient', 'mean', 'kurtosis', 'median', 'max', 'min', 'var', 'sigma']
    self._statsVectorPrefix = ['nsen', 'sen', 'pearson', 'cov', 'vsen', 'spearman']
    self._polynomialOrder = '2'
    self._sparseGridData = None
    self._data = None
    self._expTargets = None
    self._expCov = None
    self._dynamic = False
    self._initInputs = None
    self._globalSettings = {}
    self._miscDict =  {'AnalysisType':'required',
                    'limit':self._limit,
                    'Inputs':'required',
                    'Outputs':'required',
                    'pivot':self._pivot,
                    'PolynomialOrder':self._polynomialOrder,
                    'SparseGridData':self._sparseGridData,
                    'data': self._data,
                    'expTargets': self._expTargets,
                    'expCov': self._expCov,
                    'InitialInputs': self._initInputs,
                    'dynamic':self._dynamic} # dictionary stores some default values and required inputs

  def getTemplateFile(self):
    """
    """
    return self._templateFile

  def getOutput(self):
    """
      get the processed outputs from this class: PoemTemplateInterface
      @ In, None
      @ Out, (outputDict, miscDict), tuple, first dictionary contains the whole element that need to be appended in
        the templated input, while the second dictionary contains only the values that need to be replaced.
    """
    miscDict = {'limit': self._limit,
                'pivotParameter':self._pivot,
                'PolynomialOrder':self._polynomialOrder}
    return self._ravenNodeDict, miscDict

  def readInput(self):
    """
      Read the POEM input files, and construct corresponding ET elements
      @ In, None
      @ Out, None
    """
    logger.info("Start to process input file with root node: %s", self._inputRoot.tag)
    # process RunInfo
    globalSettings = self.findRequiredNode(self._inputRoot, 'GlobalSettings')
    self.readGlobalSettings(globalSettings)
    if self._dynamic:
      self._templateFile = templateConfig['templates'][self._analysisType+'_dynamic']
    else:
      self._templateFile = templateConfig['templates'][self._analysisType]
    #
    requiredNode = self.analysisRequired[self._analysisType]
    optionalNode = self.analysisOptions[self._analysisType]
    for node in requiredNode:
      xml = self.findRequiredNode(self._inputRoot, node)
      if xml is None:
        continue
      if node not in self._ravenNodeDict:
        self._ravenNodeDict[node] = [subnode for subnode in xml]
      else:
        raise IOError(f"Duplicate nodes are found in the input file {self._inputFile}")
    for node in optionalNode:
      xml = self._inputRoot.find(node)
      if xml is not None:
        self._ravenNodeDict[node] = [subnode for subnode in xml]

    if self._dynamic and self._analysisType in ['bayesian_optimization']:
      raise IOError('Not implemented for dynamic bayesian optimization yet!')

    ######################
    # Build the common blocks
    inputGroup = self.buildVariableGroup('inputGroup', self._inputVarList)
    self._variableGroupsList.append(inputGroup)
    if self._dynamic:
      outputGroup = self.buildVariableGroup('outputGroup', self._outputVarList+[self._pivot])
    else:
      outputGroup = self.buildVariableGroup('outputGroup', self._outputVarList)
    self._variableGroupsList.append(outputGroup)
    if self._analysisType == 'sensitivity':
      statsGroup = self.buildStatsGroup("statsGroup", self._inputVarList, self._outputVarList)
      self._variableGroupsList.append(statsGroup)
      if self._dynamic:
        outStatGroup = self.buildVariableGroup('outputGroup_stat', self._outputVarList)
        self._variableGroupsList.append(outStatGroup)
    self._ravenNodeDict['VariableGroups'] = self._variableGroupsList

    # build Monte Carlo Sampler
    limit = self._limit
    if self._analysisType in ['lhs', 'train_rom', 'bayesian_optimization']:
      if self._analysisType in ['bayesian_optimization']:
        limit = self._initSamples
      sampledVars = self.buildSamplerVariable(self._inputVarList, self._ravenNodeDict['Distributions'], limit=limit, grid=True)
    else:
      sampledVars = self.buildSamplerVariable(self._inputVarList, self._ravenNodeDict['Distributions'])
    if self._analysisType in ['sensitivity', 'sparse_grid_rom', 'mc']:
      mcNode = self.buildMonteCarloSampler('Sampler', self._limit)
      mcNode.extend(sampledVars)
      self._ravenNodeDict['Samplers'] = [mcNode]
    elif self._analysisType in ['lhs', 'train_rom', 'bayesian_optimization']:
      lhsNode = xmlUtils.newNode(tag='Stratified', attrib={'name':'Sampler'})
      lhsNode.extend(sampledVars)
      self._ravenNodeDict['Samplers'] = [lhsNode]

    if self._analysisType in ['sparse_grid_construction', 'sparse_grid_rom']:
      sparseGridNode = self.buildSparseGridSampler('SparseGrid')
      sparseGridNode.extend(sampledVars)
      if 'Samplers' not in self._ravenNodeDict:
        self._ravenNodeDict['Samplers'] = [sparseGridNode]
      else:
        self._ravenNodeDict['Samplers'].append(sparseGridNode)

    # build MultiRun Input
    if 'Files' in self._ravenNodeDict:
      filesList = self._ravenNodeDict['Files']
      files = [inp.attrib['name'] for inp in filesList]
      inputNodes = []
      for fname in files:
        inputNodes.append(xmlUtils.newNode(tag='Input', attrib={'class':'Files', 'type':''}, text=fname))
      self._ravenNodeDict['MultiRun'] = inputNodes

    if self._analysisType in ['sparse_grid_rom']:
      if self._sparseGridData is None:
        raise IOError('SparseGridData is required, please specify it in "GlobalSettings"')
      inputNode = xmlUtils.newNode(tag='Input', attrib={'name':'SparseGrid_data', 'type':''}, text=self._sparseGridData)
      if 'Files' not in self._ravenNodeDict:
        self._ravenNodeDict['Files'] = [inputNode]
      else:
        self._ravenNodeDict['Files'].append(inputNode)


    if self._analysisType in ['train_rom', 'bayesian_optimization']:
      if self._data is None:
        raise IOError('Training data is required, please specify it in "GlobalSettings" using subnode "data"')
      inputNode = xmlUtils.newNode(tag='Input', attrib={'name':'training_data', 'type':''}, text=self._data)
      if 'Files' not in self._ravenNodeDict:
        self._ravenNodeDict['Files'] = [inputNode]
      else:
        self._ravenNodeDict['Files'].append(inputNode)

    # build 'bayesian_optimization'
    if self._analysisType in ['bayesian_optimization']:
      bayOptNodes = []
      if len(self._outputVarList) > 1:
        raise IOError(f'Bayesian optimization currently only work with single objective, but got {self._outputVarList}')
      optVars = self.buildSamplerVariable(self._inputVarList, self._ravenNodeDict['Distributions'])
      bayOptNodes.extend(optVars)
      bayOptNodes.append(xmlUtils.newNode(tag='objective', text=self._outputVarList[0]))
      samplerInit = xmlUtils.newNode(tag='samplerInit')
      samplerInit.append(xmlUtils.newNode(tag='limit', text=self._limit))
      bayOptNodes.append(samplerInit)
      if 'Functions' in self._ravenNodeDict:
        funList = self._ravenNodeDict['Functions']
        for fun in funList:
          bayOptNodes.append(xmlUtils.newNode(tag='Constraint', attrib={'class':'Functions', 'type':'External'}, text=fun.attrib.get('name')))
      self._ravenNodeDict['BayesianOptimizer'] = bayOptNodes


    # build model_calibration
    if self._analysisType in ['model_calibration']:
      calibNode = []
      varList = self.buildSamplerVariable(self._inputVarList, self._ravenNodeDict['Distributions'], init=self._initInputs)
      calibNode.extend(varList)
      self._ravenNodeDict['AdaptiveMetropolis'] = calibNode

    self.checkInput()


  def readGlobalSettings(self, xmlNode):
    """
      Read the RunInfo XML node from the input root
      @ In, xmlNode, xml.etree.ElementTree.Element, the input root xml
      @ Out, None
    """
    logger.info("Start to read 'GlobalSettings' node")
    for key, val in self._miscDict.items():
      if val == 'required':
        node = self.findRequiredNode(xmlNode, key)
        self._globalSettings[key] = node.text
      else:
        try:
          node = self.findRequiredNode(xmlNode, key)
          self._globalSettings[key] = node.text
        except IOError:
          pass
    self._analysisType = self._globalSettings['AnalysisType'].strip().lower()
    self._inputVarList = poemUtils.convertNodeTextToList(self._globalSettings['Inputs'])
    self._outputVarList = poemUtils.convertNodeTextToList(self._globalSettings['Outputs'])
    if 'InitialInputs' in self._globalSettings:
      self._initInputs = poemUtils.convertNodeTextToFloatList(self._globalSettings['InitialInputs'])
    self._pivot = self._globalSettings.get('pivot', self._pivot)
    self._limit = self._globalSettings.get('limit', self._limit)
    if 'dynamic' in self._globalSettings:
      self._dynamic = poemUtils.convertStringToBool(self._globalSettings.get('dynamic'))
    self._polynomialOrder = self._globalSettings.get('PolynomialOrder', self._polynomialOrder)
    self._sparseGridData = self._globalSettings.get('SparseGridData', self._sparseGridData)
    self._data = self._globalSettings.get('data', self._data)

    if self._analysisType not in self.validAnalysis:
      raise IOError(f'Invalid analysis type "{self._analysisType}" provided, please choose one of "{self.validAnalysis}" instead.')

    self._miscDict.update(self._globalSettings)

  def checkInput(self):
    """
      Check the consistency of user provided inputs
      @ In, None
      @ Out, None
    """
    logger.info("Checking the consistency of user provided input")

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
  def buildHistorySet(name, inputs, outputs, pivot="time"):
    """
      Build single HistorySet XML node
      @ In, name, str, the name for the PointSet
      @ In, inputs, str, string that contains the list of input variables
      @ In, outputs, str, string that contains the list of output variables
      @ out, historySet, xml.etree.ElementTree.Element, the constructed HistorySet XML node
    """
    historySet = xmlUtils.newNode(tag='HistorySet', attrib={'name':name})
    historySet.append(xmlUtils.newNode(tag='Input', text=inputs))
    historySet.append(xmlUtils.newNode(tag='Output', text=outputs))
    options = xmlUtils.newNode(tag='options')
    options.append(xmlUtils.newNode(tag='pivotParameter', text=pivot))
    historySet.append(options)
    return historySet

  @staticmethod
  def buildPrint(name, source):
    """
      Build single OutStream Print XML node
      @ In, name, str, the name for the PointSet
      @ In, source, str, string that contains name of Data Object
      @ out, printObj, xml.etree.ElementTree.Element, the constructed print XML node
    """
    printObj = xmlUtils.newNode(tag='Print', attrib={'name':name})
    printObj.append(xmlUtils.newNode(tag='type', text='csv'))
    printObj.append(xmlUtils.newNode(tag='source', text=source))
    printObj.append(xmlUtils.newNode(tag='what', text='input,output'))
    return printObj

  def buildSamplerVariable(self, inputs, distNode, limit=20, grid=False, init=None):
    """
      build the sampler variable block
    """
    varDistList = []
    varNodeList = []
    for subnode in distNode:
      varDistList.append(subnode.attrib['name'])
    for i, inp in enumerate(inputs):
      if inp not in varDistList:
        raise IOError(f'Distribution of variable {inp} is not defined in <Distribution> block!')
      varNode = xmlUtils.newNode(tag='variable', attrib={'name':inp})
      varNode.append(xmlUtils.newNode(tag='distribution', text=inp))
      if init:
        varNode.append(xmlUtils.newNode(tag='initial', text=str(init[i])))
      if grid:
        varNode.append(xmlUtils.newNode(tag='grid', attrib={'construction':'equal', 'steps':limit, 'type':'CDF'}, text='0.0 1.0'))
      varNodeList.append(varNode)
    return varNodeList

  @staticmethod
  def buildSparseGridSampler(name='SparseGrid'):
    """
    """
    sgNode = xmlUtils.newNode(tag='SparseGridCollocation', attrib={'name':name})
    sgNode.append(xmlUtils.newNode(tag='ROM', attrib={'class':'Models', 'type':'ROM'}, text='SparseGridRom'))
    return sgNode

  @staticmethod
  def buildMonteCarloSampler(name, limit):
    """
    """
    mcNode = xmlUtils.newNode(tag='MonteCarlo', attrib={'name':name})
    samplerInit = xmlUtils.newNode(tag='samplerInit')
    samplerInit.append(xmlUtils.newNode(tag='limit', text=limit))
    mcNode.append(samplerInit)
    return mcNode

  @staticmethod
  def buildVariableGroup(name, varList):
    """
      Build variable group node
      @ In, name, str, the name for the variable group
      @ In, varList, list, list of variables
      @ out, group, xml.etree.ElementTree.Element, the constructed variable group XML node
    """
    if isinstance(varList, str):
      text = vars
    elif isinstance(varList, list):
      text = ','.join(varList)
    else:
      raise IOError(f'Can not accept input "{varList}" with type {type(varList)}, only accept "str" or "list"!')
    group = xmlUtils.newNode(tag='Group', attrib={'name':name}, text=text)
    return group

  def buildStatsGroup(self, name, inputs, outputs):
    """
      Build basic statistic variable group node
      @ In, name, str, the name for the variable group
      @ In, inputs, list, list of input variables
      @ In, outputs, list, list of output variables
      @ out, group, xml.etree.ElementTree.Element, the constructed variable group XML node
    """
    varList = []
    for prefix in self._statsPrefix:
      varList.extend([prefix+"_"+out for out in outputs])
    for prefix in self._statsVectorPrefix:
      for out in outputs:
        varList.extend([prefix+"_"+out+"_"+inp for inp in inputs])
    group = self.buildVariableGroup(name, varList)
    return group


  @staticmethod
  def findRequiredNode(xmlNode, nodeTag):
    """
      Find the required xml node
      @ In, xmlNode, xml.etree.ElementTree.Element, xml element node
      @ In, nodeTag, str, node tag that is used to find the node
      @ Out, subnode, xml.etree.ElementTree.Element, xml element node
    """
    subnode = xmlNode.find(nodeTag)
    if subnode is None and nodeTag not in ['RunInfo', 'Files']:
      raise IOError('Required node ' + nodeTag + ' is not found in the input file!')
    return subnode

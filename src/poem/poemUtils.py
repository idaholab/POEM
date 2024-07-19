# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
"""
  Created on April 1, 2024
  @author: wangc
"""
#External Modules------------------------------------------------------------------------------------
import logging
#External Modules End--------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

def convertNodeTextToList(nodeText, sep=None):
  """
    Convert space or comma separated string to list of string
    @ In, nodeText, str, string from xml node text
    @ Out, listData, list, list of strings
  """
  listData = None
  if sep is None:
    if ',' in nodeText:
      listData = list(elem.strip() for elem in nodeText.split(','))
    else:
      listData = list(elem.strip() for elem in nodeText.split())
  else:
    listData = list(elem.strip() for elem in nodeText.split(sep))
  return listData

def convertNodeTextToFloatList(nodeText, sep=None):
  """
    Convert space or comma separated string to list of float
    @ In, nodeText, str, string from xml node text
    @ Out, listData, list, list of floats
  """
  listData = None
  if sep is None:
    if ',' in nodeText:
      listData = list(float(elem) for elem in nodeText.split(','))
    else:
      listData = list(float(elem) for elem in nodeText.split())
  else:
    listData = list(elem.strip() for elem in nodeText.split(sep))
  return listData

def convertStringToFloat(xmlNode):
  """
    Convert xml node text to float
    @ In, xmlNode, xml.etree.ElementTree.Element, xml element
    @ Out, val, float, value of xml element text
  """
  try:
    val = float(xmlNode.text)
    return val
  except (ValueError,TypeError):
    raise IOError('Real value is required for content of node %s, but got %s' %(node.tag, node.text))

def convertStringToInt(xmlNode):
  """
    Convert xml node text to integer.
    @ In, xmlNode, xml.etree.ElementTree.Element, xml element
    @ Out, val, integer, value of xml element text
  """
  try:
    val = int(xmlNode.text)
    return val
  except (ValueError,TypeError):
    raise IOError('Integer value is required for content of node %s, but got %s' %(node.tag, node.text))

def toString(s):
  """
    Method aimed to convert a string in type str
    @ In, s, string,  string to be converted
    @ Out, s, string, the casted value
  """
  if type(s) == type(""):
    return s
  else:
    return s.decode()

def convertStringToBool(nodeText):
  """
    Convert string to bool
    @ In, nodeText, str, string from xml node text
    @ Out, val, bool, True or False
  """
  stringsThatMeanTrue = list(['yes','y','true','t','on'])
  val = False
  if nodeText.lower() in stringsThatMeanTrue:
    val = True
  return val

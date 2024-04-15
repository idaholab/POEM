"""
Created on April 1, 2024
@author: wangc

This module is the POEM Template interface, which use the user provided input XML
file to construct the corresponding RAVEN workflows i.e. RAVEN input XML file.
"""
import os
import logging
import argparse

from src.poem.PoemTemplate import PoemTemplate
from src.poem.PoemTemplateInterface import PoemTemplateInterface

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


if __name__ == '__main__':
  logger.info('Welcome to the POEM!')
  parser = argparse.ArgumentParser(description='POEM Templated RAVEN Runner')
  parser.add_argument('-i', '--input', nargs=1, required=True, help='POEM input filename')
  # parser.add_argument('-t', '--template', nargs=1, required=True, help='POEM template filename')
  parser.add_argument('-o', '--output', nargs=1, help='POEM output filename')

  args = parser.parse_args()
  args = vars(args)
  inFile = args['input'][0]
  logger.info('POEM input file: %s', inFile)
  # tempFile = args['template'][0]
  # logger.info('POEM template file: %s', tempFile)
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
  tempFile = templateInterface.getTemplateFile()

  # create template class instance
  templateClass = PoemTemplate()
  # load template
  templateClass.loadTemplate(tempFile)
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

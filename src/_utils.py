# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
"""
  utilities for use within POEM
"""
import os
from os import path
import sys
import importlib
import xml.etree.ElementTree as ET

def get_raven_loc():
  """
    Return RAVEN location: read from POEM/.ravenconfig.xml
    @ In, None
    @ Out, loc, string, absolute location of RAVEN
  """
  try:
    import ravenframework
    return path.dirname(ravenframework.__path__[0])
  except ModuleNotFoundError:
    pass
  config = os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '.ravenconfig.xml'))
  if not os.path.isfile(config):
    raise IOError('POEM config file not found at "{}"! Has POEM been installed as a plugin in a RAVEN installation?'
                  .format(config))
  loc = ET.parse(config).getroot().find('FrameworkLocation')
  assert loc is not None and loc.text is not None
  return path.abspath(path.dirname(loc.text))

def get_plugin_loc(plugin, raven_path=None):
  """
    Get plugin location in installed RAVEN
    @ In, plugin, string, the plugin name
    @ In, raven_path, string, optional, if given then start with this path
    @ Out, plugin_loc, string, location of plugin
  """
  if plugin == 'POEM':
    return path.abspath(path.join(__file__, '..', '..'))
  else:
    if raven_path is None:
      raven_path = get_raven_loc()
    plugin_handler_dir = os.path.join(raven_path, '..', 'scripts')
    sys.path.append(plugin_handler_dir)
    plugin_handler = importlib.import_module('plugin_handler')
    sys.path.pop()
    plugin_loc = plugin_handler.getPluginLocation(plugin)
    return plugin_loc

if __name__ == '__main__':
  argvs = sys.argv[1:]
  if len(argvs) == 0:
    raise IOError('No action is provided, please use "get_raven_loc" or "get_plugin_loc" for command line argument.')
  action = None
  plugin = None
  if len(argvs) < 2:
    action = argvs[0]
  else:
    action, plugin = argvs[0], argvs[1]
  if action == 'get_raven_loc':
    print(get_raven_loc())
  elif action == 'get_plugin_loc' and plugin is not None:
    print(get_plugin_loc(plugin))
  else:
    raise IOError('Unrecognized action: "{}"'.format(action))

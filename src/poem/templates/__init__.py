# Copyright 2024, Battelle Energy Alliance, LLC  ALL RIGHTS RESERVED

import pathlib
import tomli
import os

configFileName = 'config.toml'

path = pathlib.Path(os.path.join(pathlib.Path(__file__).parent, configFileName))
with path.open(mode="rb") as fp:
  templateConfig = tomli.load(fp)
  for file in templateConfig['templates']:
    templateConfig['templates'][file] = os.path.join(os.path.dirname(__file__), templateConfig['templates'][file])

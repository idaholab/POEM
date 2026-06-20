============
Installation
============

How to install?
---------------

Installation
++++++++++++

Install the released package from PyPI:

.. code:: bash

  uv venv --python 3.11
  source .venv/bin/activate
  uv pip install poem-ravenframework

Clone
+++++

.. code:: bash

  git clone git@github.com:idaholab/POEM.git
  cd POEM
  uv sync --python 3.11
  source .venv/bin/activate

The ``uv sync`` command creates ``.venv``, installs POEM in editable mode, and installs
the runtime dependencies listed in ``pyproject.toml``.

Build Documentation
+++++++++++++++++++

.. code:: bash

  uv sync --python 3.11 --extra docs
  source .venv/bin/activate
  cd docs
  make html


Test
++++

.. code:: bash

  cd POEM/tests
  poem -i lhs_sampling.xml

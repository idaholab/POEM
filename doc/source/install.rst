============
Installation
============

How to install?
---------------------------------------

Installation
+++++++++++++++++++++++++++++++++++++++

.. code:: bash

  conda create -n poem_libs python=3.10
  conda activate poem_libs
  pip install raven-framework baycal-ravenframework

Test
++++++++++++++++++++++++++++++++++++++++

.. code:: bash

  cd POEM/tests
  python ../poem.py -i lhs_sampling.xml
  raven_framework raven_lhs_sampling.xml

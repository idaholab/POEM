.. _quickstart:

Quick Start
===========

Introduction
++++++++++++

POEM is a platform for optimal experiment management, powered with automated machine
learning to accelerate the discovery of optimal solutions, and automatically guide
the design of experiments to be evaluated. POEM currently supports 1) random model
explorations for experiment design, 2) sparse grid model explorations with Gaussian
Polynomial Chaos surrogate model to accelerate experiment design ,3) time-dependent
model sensitivity and uncertainty analysis to identify the importance features for
experiment design, 4) model calibrations via Bayesian inference to integrate experiments
to improve model performance, and 5) Bayesian optimization for optimal experimental design.
In addition, POEM aims to simplify the process of experimental design for users,
enabling them to analyze the data with minimal human intervention, and improving
the technological output from research activities.

POEM leverages RAVEN (a robust platform to support model explorations and decision making)
to allow for large scalability and reduction of the computational costs and provides
access to complex physical models while performing optimal experimental design.

Input Structure
+++++++++++++++

POEM utilizes XML to define its input structure. The main input blocks are as follows:

Simulation block
^^^^^^^^^^^^^^^^
The root node containing the entire input, all of the following blocks fit inside
the ``Simulaiton`` block

.. code:: xml

  <Simulation>

    <RunInfo>
      ...
    </RunInfo>

    <GlobalSettings>
      ...
    </GlobalSettings>

    <Distributions>
      ...
    </Distributions>

    <Models>
      ...
    </Models>

    <Files>
      ...
    </Files>

    <Functions>
      ...
    </Functions>

    <LikelihoodModel>
      ...
    </LikelihoodModel>

  </Simulation>

GlobalSettings block
^^^^^^^^^^^^^^^^^^^^
Specifies the global settings for the calculations. For example:

.. code:: xml

  <GlobalSettings>
    <!-- Required Nodes -->
    <AnalysisType>LHS</AnalysisType>
    <limit>10</limit>
    <Inputs>x, y</Inputs>
    <Outputs>OutputPlaceHolder</Outputs>

    <!-- Optional Nodes -->
    <pivot>time</pivot>
    <dynamic>True</dynamic>

    <!-- Optional Nodes, uses for certain analysis -->
    <SparseGridData>path/to/data.csv</SparseGridData>
    <data>path/to/data.csv</data>
    <InitialInputs>0.1, 4.0, -1.0</InitialInputs>
    <PolynomialOrder>3</PolynomialOrder>
  </GlobalSettings>

**In general, this block accepts the following subnodes:**

* Required Nodes

  * ``AnalysisType``: The type of analysis, it accepts the following keywords:

    * ``mc``: Simple Monte Carlo analysis for given model. See :ref:`mc`.

    * ``lhs``: Sample given model using Latin Hyper-cube Sampling (LHS) strategy. See :ref:`lhs`.

    * ``sensitivity``: Perform sensitivity analysis for given model. The ``mean, variance, 95/95 percentile, correlation, spearman correlation, sensitivity coefficients, etc.`` will be computed. See :ref:`sen`.

    * ``sparse_grid_construction``: Generate sparse grid locations to guide experiments. These locations can be used to efficiently construct high-order Gaussian Polynomial Chaos surrogate model. See :ref:`sparsegrid`.

    * ``sparse_grid_rom``: Train a multi-variate high-order Gaussian Polynomial Chaos ROM/surrogate based on user provided experimental data. See :ref:`rom`.

    * ``train_rom``: Train a Gaussian Process ROM based on user provided data. See :ref:`rom`.

    * ``bayesian_optimization``: Perform Bayesian optimization based on user provided data and simulation model. See :ref:`bayopt`.

    * ``model_calibration``: Perform model calibration utilizing Bayesian inference based on user provided data and simulation model. See :ref:`cal`.

  * ``limit``: The total number of model executions or the number of samples to generate.

  * ``Inputs``: The list of input variables

  * ``Outputs``: The list of output variables. If no output variables, ``OutputPlaceHolder`` can be used.

* Optional Nodes

  * ``dynamic``: True if the user wants to perform time-dependent analysis, such as time-dependent ROM construction, sensitivity analysis, model calibration etc.

  * ``pivot``: Required if ``dynamic`` is True. The pivot variable for dynamic analysis. Default is ``time``.

* Optional Nodes for Certain Analysis

  * ``SparseGridData``: The experimental data that can be used to train Gaussian Polynomial Chaos ROM. Only used by ``sparse_grid_construction`` and ``sparse_grid_rom``.

  * ``PolynomialOrder``: The highest order for the Gaussian Polynomial Chaos ROM. Only used by ``sparse_grid_construction`` and ``sparse_grid_rom``

  * ``data``: The experimental data that can be used to train Gaussian Process ROM. Only used by ``train_rom`` and ``bayesian_optimization``.

  * ``InitialInputs``: The initial values for the input variables listed by ``<Inputs>`` in the ``<GlobalSettings>``

RunInfo block
^^^^^^^^^^^^^
Specifies the calculation settings (woring directory, number of parallel simulations, etc.)

.. code:: xml

  <RunInfo>
    <WorkingDir>LHS</WorkingDir>
    <batchSize>1</batchSize>
  </RunInfo>

**In general, this block accepts the following subnodes:**

* ``WorkingDir``: specifies the absolute or relative path to a directory that will store all the
  results of the calculations.

* ``batchSize``: specifies the number of parallel executed simultaneously.

* ``JobName``: specifies the name to use for the job when submitting to a pbs queue.

**RunInfo for Cluster Usage**

.. code:: xml

  <RunInfo>
    <WorkingDir>FirstMF</WorkingDir>
    <batchSize>3</batchSize>
    <clusterParameters>-W block=true</clusterParameters>
    <NumThreads>4</NumThreads>
    <mode>
      mpi
      <runQSUB/>
    </mode>
    <NodeParameter> </NodeParameter>
    <NumMPI>2</NumMPI>
    <expectedTime>0:10:00</expectedTime>
    <JobName>test_qsub</JobName>
  </RunInfo>

Files block
^^^^^^^^^^^
Specifies the files to be used for the <Models> block as input. Users can specify
as many input files as they need, and utilize <Input> node to specify the ``name``,
and the ``path/to/file``.

.. code:: xml

  <Files>
    <Input name="sauq" type="">../../models/sauq.m</Input>
    <Input name="rt" type="">../../models/RateTheory.m</Input>
    <Input name="kc" type="">../../models/KlemensCallawayModel.m</Input>
  </Files>



Distributions block
^^^^^^^^^^^^^^^^^^^
POEM leverages RAVEN (https://github.com/idaholab/raven) input structure to build customized workflows
for model explorations and optimal experiment design. In this case, POEM provides support for all the
probability distributions available in RAVEN. The following are the example for the *Distributions* block.

.. code:: xml

  <Distributions>
    <Uniform name='x'>
      <lowerBound>-10</lowerBound>
      <upperBound>0</upperBound>
    </Uniform>
    <Uniform name='y'>
      <lowerBound>-6.5</lowerBound>
      <upperBound>0</upperBound>
    </Uniform>
  </Distributions>

In this block, the users need to define ``distribution`` for each variables listed in
``GlobalSettings`` ``Inputs`` node, and ``name`` for the distribution should match the variable
name listed under ``<GlobalSettings><Inputs>VariableList</Inputs></GlobalSettings>``.


Models block
^^^^^^^^^^^^
Similar to ``<Distributions>`` block, POEM leverages RAVEN (https://github.com/idaholab/raven) ``<Models>``
input structure. In this case, POEM provides support for all the
models available in RAVEN. The following are the example for the *Models* block.

.. code:: xml

  <Models>
    <ExternalModel ModuleToLoad="../../models/mishraBirdConstrained.py" name="mishra" subType="">
      <inputs>x, y</inputs>
      <outputs>z</outputs>
    </ExternalModel>
  </Models>

As the name suggests, an external model is an entity that is embedded at run time.
This object allows the user to create a python module that is going to be
treated as a predefined internal model object.

The specifications of an External Model must be defined within the XML block
``<ExternalModel>``. This blocks accepts the following subnodes:

* ``inputs``: Each variable name needs to match a variable used/defined in the external python model.

* ``outputs``: Each variable name needs to match a variable used/defined in the external python model.

Each variable defined in the ``<ExternalModel>`` ``<inputs>`` and ``<outputs>`` block is available in the
module (each method implemented) as a python ``self.`` member.


Functions block
^^^^^^^^^^^^^^^
POEM leverages RAVEN (https://github.com/idaholab/raven) ``<Functions>``
input structure. In this case, POEM provides support for the usage of user-defined external
functions. These functions are python modules, with a format is automatically interpretable by
RAVEN software.

The following are the example for the *Functions* block.

.. code:: xml

  <Functions>
    <External file="../../models/mishraBirdConstrained.py" name="constraint1">
      <variables>x,y</variables>
    </External>
  </Functions>

In this section, the XML input syntax and the format of the accepted functions
are fully specified. The specifications of an external function must be defined
within the XML ``<External>`` block. This XML node requires the following attributes:

* ``name``: user-defined name of this function.

* ``file``: absolute or relative path specifying the code associated to this function.

In order to make the code aware of the variables the user is going to
manipulate/use in her/his own python function, the variables need to be
specified in the ``<variables>`` subnode input block. The user needs to input,
within this block, only the variables directly used by the external function.

When the external function variables are defined, at runtime, the code initializes
them and keeps track of their values during the simulation.
Each variable defined in the ``<variables>`` block is available in the
function as a python **self.** member. In the following, an example of a
user-defined external function is reported. The method ``evaluate`` needs to be defined
in the function file.

.. code:: python

  def evaluate(self):
    return self.a * self.c


LikelihoodModel block for Model Calibration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This node is only used by model calibration analysis. An example is presented:

.. code:: xml

  <LikelihoodModel>
    <simTargets>eta</simTargets>
    <expTargets shape="1,50" computeCov='False' correlation='False'>
      -1.16074224 -1.10303445 -1.02830511 -0.89782965 -0.73765453 -0.7989537
       -0.86163706 -1.02209944 -1.12444044 -1.23657398 -1.16081758 -1.01219869
       -0.890747   -0.80444122 -0.70893668 -0.61012531 -0.65670863 -0.6768583
       -0.74732441 -0.81448647 -0.73232671 -0.54989334 -0.39796749 -0.07894291
        0.13067378  0.28999998  0.27418965  0.313329    0.32306704  0.2885684
        0.32736775  0.52458854  0.69446572  0.82419521  1.04393683  1.00435818
        1.0810376   0.97245373  0.82406522  0.76067559  0.70145544  0.79479965
        0.88035895  0.97750307  1.11524353  1.17159017  1.18299222  1.07255006
        1.02835909  0.90784132
    </expTargets>
    <expCov diag="True">
         0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
         0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
         0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
         0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
         0.02, 0.02, 0.02, 0.02, 0.02, 0.02
    </expCov>
    <!-- <biasTargets></biasTargets>
    <biasCov diag="False"></biasCov> -->
    <!-- <romCov diag="True"></romCov> -->
  </LikelihoodModel>

The ``<LikelihoodModel>`` node accepts the following subnodes:

* ``simTargets``: Targets of simulations that are used in the calibration.

* ``expTargets``: Targets of experiments that are used in the calibration. Either variables or list of values. This node accepts the following attributes:

  * ``shape``: determine the number of targets and the number of experimental observations for each targets. For example, ``shape="3,2"`` will indicate 2 targets and 3 observations for each targets. While ``shape="10"`` will indicate one target with 10 observations. Omitting this optional attribute will result a single target with multiple observations instead.

  * ``computeCov``: Indicate whether the experiment covariance matrix is provided or computed based on given experiment observations. If True, we will compute the covariance based on given observations, else, the user need to provide the covariance matrix.

  * ``correlation``: Indicate whether the targets are correlated or not. If True, and ``compute`` is True, we will compute the covariance matrix, elif False and ``compute`` is True, we will only compute the variance of each target.

* ``expCov``: Experiment covariance, i.e. measurement noise. This node accepts the following attribute:

  * ``diag``: If True, only variance for each target is required to provide, else, the user need to provide the full covariance matrix.

* ``biasTargets``: Model uncertainty/discrepancy/bias/error in Targets that are used in calibration

* ``biasCov``: Model covariance, model bias/discrepancy or model inadequacy caused by missing physics or numerical approximation. This node accepts the following attribute:

  * ``diag``: If True, only variance for each target is required to provide, else, the user need to provide the full covariance matrix.

* ``romCov``: Model uncertainty caused by surrogate model, such as interpolation. This node accepts the following attribute:

  * ``diag``: If True, only variance for each target is required to provide, else, the user need to provide the full covariance matrix.

* ``reduction``: Allows reduction on likelihood model construction. This node accepts the following attributes:

  * ``type``: The method used for reduction, default is **PCA**

  * ``basis``: user provided basis vector for reduction

  * ``shape``: determine the basis vectors for reduction. For example, ``shape="10,2"`` will indicate 2 basis vectors with dimension 10

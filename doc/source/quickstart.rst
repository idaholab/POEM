.. _quickstart:

Quick Start
===========

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

POEM Input Structure:
+++++++++++++++++++++

POEM utilizes XML to define its input structure. The main input blocks are as follows:

<Simulation> block:
^^^^^^^^^^^^^^^^^^^
The root node containing the entire input, all of the following blocks fit inside
the ``Simulaiton`` block

.. code:: xml

  <Simulation>
    ...
  </Simulation>

<GlobalSettings> block:
^^^^^^^^^^^^^^^^^^^^^^^
Specifies the global settings for the calculations. In general, this block accepts
the following subnodes:

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

* Required Nodes

  * ``AnalysisType``: The type of analysis, it accepts the following keywords:

    * ``mc``: Simple Monte Carlo analysis for given model.

    * ``lhs``: Sample given model using Latin Hyper-cube Sampling (LHS) strategy.

    * ``sensitivity``: Perform sensitivity analysis for given model. The ``mean, variance, 95/95 percentile, correlation, spearman correlation, sensitivity coefficients, etc.`` will be computed.

    * ``sparse_grid_construction``: Generate sparse grid locations to guide experiments. These locations can be used to efficiently construct high-order Gaussian Polynomial Chaos surrogate model.

    * ``sparse_grid_rom``: Train a multi-variate high-order Gaussian Polynomial Chaos ROM/surrogate based on user provided experimental data.

    * ``train_rom``: Train a Gaussian Process ROM based on user provided data.

    * ``bayesian_optimization``: Perform Bayesian optimization based on user provided data and simulation model.

    * ``model_calibration``: Perform model calibration utilizing Bayesian inference based on user provided data and simulation model.

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

<RunInfo> block:
^^^^^^^^^^^^^^^^
Specifies the calculation settings (woring directory, number of parallel simulations, etc.)

.. code:: xml

  <RunInfo>
    <WorkingDir>LHS</WorkingDir>
    <batchSize>1</batchSize>
  </RunInfo>

<Files> block:
^^^^^^^^^^^^^^
Specifies the files to be used for the <Models> block as input. Users can specify
as many input files as they need, and utilize <Input> node to specify the ``name``,
and the ``path/to/file``.

.. code:: xml

  <Files>
    <Input name="sauq" type="">../../models/sauq.m</Input>
    <Input name="rt" type="">../../models/RateTheory.m</Input>
    <Input name="kc" type="">../../models/KlemensCallawayModel.m</Input>
  </Files>



<Distributions> block:
^^^^^^^^^^^^^^^^^^^^^^

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


<Models> block:
^^^^^^^^^^^^^^^

.. code:: xml

  <Models>
    <ExternalModel ModuleToLoad="../../models/mishraBirdConstrained.py" name="mishra" subType="">
      <inputs>x, y</inputs>
      <outputs>z</outputs>
    </ExternalModel>
  </Models>

<Functions> block:
^^^^^^^^^^^^^^^^^^


.. code:: xml

  <Functions>
    <External file="../../models/mishraBirdConstrained.py" name="constraint1">
      <variables>x,y</variables>
    </External>
  </Functions>


<LikelihoodModel> block for Model Calibration:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


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


Random model explorations for experiment design:
++++++++++++++++++++++++++++++++++++++++++++++++

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation>
    <RunInfo>
      <WorkingDir>LHS</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>LHS</AnalysisType>
      <limit>10</limit>
      <Inputs>x, y</Inputs>
      <Outputs>OutputPlaceHolder</Outputs>
    </GlobalSettings>

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

  </Simulation>

Sparse grid model explorations with Gaussian Polynomial Chaos surrogate model to accelerate experiment design:
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Sparse grid model construction

.. code:: xml

  <Simulation>
    <RunInfo>
      <WorkingDir>SparseGrid</WorkingDir>
      <Sequence>SparseGridSampler, print</Sequence>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>sparse_grid_construction</AnalysisType>
      <Inputs>x, y</Inputs>
      <Outputs>z1</Outputs>
      <PolynomialOrder>3</PolynomialOrder>
    </GlobalSettings>

    <Distributions>
      <Uniform name="x">
        <lowerBound>-10</lowerBound>
        <upperBound>10</upperBound>
      </Uniform>
      <Uniform name="y">
        <lowerBound>-10</lowerBound>
        <upperBound>10</upperBound>
      </Uniform>
    </Distributions>

    <Models>
      <ExternalModel ModuleToLoad="../models/matyas" name="externalModel" subType="">
        <inputs>x, y</inputs>
        <outputs>z1</outputs>
      </ExternalModel>
    </Models>

  </Simulation>



Time-dependent model sensitivity and uncertainty analysis to identify the importance features for experiment design:
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation>
    <RunInfo>
      <JobName>sauq</JobName>
      <WorkingDir>sauq_dynamic_external</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>sensitivity</AnalysisType>
      <limit>10</limit>
      <Inputs>x0, y0, z0</Inputs>
      <pivot>time</pivot>
      <dynamic>True</dynamic>
      <Outputs>x,y,z</Outputs>
    </GlobalSettings>

    <Distributions>
      <Normal name="x0">
        <mean>4</mean>
        <sigma>1</sigma>
      </Normal>
      <Normal name="y0">
        <mean>4</mean>
        <sigma>1</sigma>
      </Normal>
      <Normal name="z0">
        <mean>4</mean>
        <sigma>1</sigma>
      </Normal>
    </Distributions>

    <Models>
      <ExternalModel ModuleToLoad="../models/lorentzAttractor.py" name="lorentzAttractor" subType="">
        <inputs>inputGroup</inputs>
        <outputs>outputGroup</outputs>
      </ExternalModel>
    </Models>

  </Simulation>

Model calibrations via Bayesian inference to integrate experiments to improve model performance:
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation verbosity="debug">

    <RunInfo>
      <WorkingDir>calibration_dynamic</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>model_calibration</AnalysisType>
      <pivot>time</pivot>
      <dynamic>True</dynamic>
      <limit>100</limit>
      <Inputs>alpha, beta, gamma</Inputs>
      <InitialInputs>0.1, 4.0, -1.0</InitialInputs>
      <Outputs>eta</Outputs>
    </GlobalSettings>

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

    <Distributions>
      <Uniform name='alpha'>
        <lowerBound>0.1</lowerBound>
        <upperBound>0.3</upperBound>
      </Uniform>
      <Uniform name='beta'>
        <lowerBound>4</lowerBound>
        <upperBound>6</upperBound>
      </Uniform>
      <Uniform name='gamma'>
        <lowerBound>-1</lowerBound>
        <upperBound>1</upperBound>
      </Uniform>
    </Distributions>

    <Models>
      <ExternalModel ModuleToLoad="../models/model_cal" name="model" subType="">
        <inputs>inputGroup</inputs>
        <outputs>outputGroup</outputs>
      </ExternalModel>
    </Models>

  </Simulation>

Bayesian optimization for optimal experimental design:
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation verbosity="debug">
    <RunInfo>
      <WorkingDir>Optimization</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>bayesian_optimization</AnalysisType>
      <data>../LHS_mishra/sampling_dump.csv</data>
      <limit>10</limit>
      <Inputs>x, y</Inputs>
      <Outputs>z</Outputs>
    </GlobalSettings>

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

    <Models>
      <ExternalModel ModuleToLoad="../../models/mishraBirdConstrained.py" name="mishra" subType="">
        <inputs>x, y</inputs>
        <outputs>z</outputs>
      </ExternalModel>

    </Models>

    <Functions>
      <External file="../../models/mishraBirdConstrained.py" name="constraint1">
        <variables>x,y</variables>
      </External>
    </Functions>

  </Simulation>








The POEM code has several fixed calculation flows.

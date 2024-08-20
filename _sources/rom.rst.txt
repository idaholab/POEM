.. _rom:

Train ROM
=========

Train reduced order models (ROM) or machine learning models based on experiment data, or mixed
experiment data and simulation data.

Train Gaussian Process Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this analysis, set ``<AnalysisType>train_rom</AnalysisType>``. For example, The following input will utilize
data provided by ``<data>`` node to train Gaussian Process Model. After training, the inputs of the Gaussian Process Model
will be sampled via Latin Hypercube Sampling algorithm with their associated distributions, and the number of samples is equal to
``<limit>`` value.

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation>
    <RunInfo>
      <WorkingDir>GP</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>train_rom</AnalysisType>
      <data>../LHS/sampling_dump.csv</data>
      <limit>10</limit>
      <Inputs>x, y</Inputs>
      <Outputs>z1</Outputs>
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

Train Dynamic Gaussian Process Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When a dynamic model is provided, the users need to set ``<pivot>`` and ``<dynamic>`` node in the
``<GlobalSettings>``. As illustrated in the following example.
In addition, set ``<AnalysisType>train_rom</AnalysisType>``. For example, The following input will utilize
data provided by ``<data>`` node to train Gaussian Process Model. After training, the inputs of the Gaussian Process Model
will be sampled via Latin Hypercube Sampling algorithm with their associated distributions, and the number of samples is equal to
``<limit>`` value.

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation>
    <RunInfo>
      <WorkingDir>GP_dynamic</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>train_rom</AnalysisType>
      <data>../LHS/sampling_dynamic_dump.csv</data>
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


Train Gaussian Polynomial Chaos Model with Sparse Grid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this analysis, set ``<AnalysisType>sparse_grid_rom</AnalysisType>``.
For example, The following input will utilize
data provided by ``<SparseGridData>`` node to train Gaussian Polynomial Chaos Model.
After training, the inputs of the Gaussian Process Model
will be sampled via Monte Carlo Sampling algorithm with their associated distributions,
and the number of samples is equal to ``<limit>`` value.

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation>

    <GlobalSettings>
      <AnalysisType>sparse_grid_rom</AnalysisType>
      <Inputs>x, y</Inputs>
      <Outputs>z1</Outputs>
      <PolynomialOrder>2</PolynomialOrder>
      <limit>10</limit>
      <SparseGridData>dump_SparseGrid.csv</SparseGridData>
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

For this ROM, the users can also set the highest order of the Gaussian Polynomial Chaos expansions.
Just set ``<PolynomialOrder>`` in ``<GlobalSettings>``.

Train Dynamic Gaussian Polynomial Chaos Model with Sparse Grid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When a dynamic model is provided, the users need to set ``<pivot>`` and ``<dynamic>`` node in the
``<GlobalSettings>``. As illustrated in the following example.
In this analysis, set ``<AnalysisType>sparse_grid_rom</AnalysisType>``.
For example, The following input will utilize
data provided by ``<SparseGridData>`` node to train Gaussian Polynomial Chaos Model.
After training, the inputs of the Gaussian Process Model
will be sampled via Monte Carlo Sampling algorithm with their associated distributions,
and the number of samples is equal to ``<limit>`` value.

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation>
    <RunInfo>
      <WorkingDir>SparseGridDynamic</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>sparse_grid_rom</AnalysisType>
      <Inputs>x0, y0, z0</Inputs>
      <pivot>time</pivot>
      <dynamic>True</dynamic>
      <Outputs>x,y,z</Outputs>
      <PolynomialOrder>2</PolynomialOrder>
      <limit>10</limit>
      <SparseGridData>../SparseGrid/SparseGrid_dynamic_dump.csv</SparseGridData>
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

For this ROM, the users can also set the highest order of the Gaussian Polynomial Chaos expansions.
Just set ``<PolynomialOrder>`` in ``<GlobalSettings>``.

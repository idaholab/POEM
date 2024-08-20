.. _sparsegrid:

Generate Sparse Grid Locations
==============================
Sparse grid model explorations with Gaussian Polynomial Chaos surrogate model to accelerate experiment design:

When generating sparse grid locations, the users can also set the highest order of the Gaussian Polynomial Chaos expansions.
The higher of the Polynomial order, the more sparse grid locations will be generated.
Just set ``<PolynomialOrder>`` in ``<GlobalSettings>``.

Once the experiment data are generated at given sparse grid locations, the Gaussian Polynomial Chaos surrogate
can be automatically constructed. See the ``Train ROM`` section on how to train Gaussian Polynomial Chaos surrogate
model.

Static Model
^^^^^^^^^^^^

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

Dynamic Model
^^^^^^^^^^^^^
When a dynamic model is provided, the users need to set ``<pivot>`` and ``<dynamic>`` node in the
``<GlobalSettings>``. As illustrated in the following example.

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation>
    <RunInfo>
      <WorkingDir>SparseGrid</WorkingDir>
      <Sequence>SparseGridSampler, print</Sequence>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>sparse_grid_construction</AnalysisType>
      <Inputs>x0, y0, z0</Inputs>
      <pivot>time</pivot>
      <dynamic>True</dynamic>
      <Outputs>x,y,z</Outputs>
      <PolynomialOrder>3</PolynomialOrder>
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

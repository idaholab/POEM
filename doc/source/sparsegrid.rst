.. _sparsegrid:

Sparse Grid Sampling
====================
Sparse grid model explorations with Gaussian Polynomial Chaos surrogate model to accelerate experiment design:


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

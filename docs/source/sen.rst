.. _sen:

Sensitivity Analysis
====================

Static Sensitivity Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this analysis, set ``<AnalysisType>sensitivity</AnalysisType>``. A Monte Carlo method will
be utilized to sample the given model with ``<limit>`` number.

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation>
    <RunInfo>
      <JobName>sauq</JobName>
      <WorkingDir>sauq_runs</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>sensitivity</AnalysisType>
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

    <Models>
      <ExternalModel ModuleToLoad="../models/matyas" name="externalModel" subType="">
        <inputs>x, y</inputs>
        <outputs>z1</outputs>
      </ExternalModel>
    </Models>

  </Simulation>


Dynamic Sensitivity Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Time-dependent model sensitivity and uncertainty analysis to identify the importance features for experiment design:
In this analysis, set ``<AnalysisType>sensitivity</AnalysisType>``. A Monte Carlo method will
be utilized to sample the given model with ``limit`` number.
When a dynamic model is provided, the users need to set ``<pivot>`` and ``<dynamic>`` node in the
``<GlobalSettings>``. As illustrated in the following example.

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

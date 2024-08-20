.. _lhs:

Latin Hypercube Sampling
========================
Utilize Latin Hypercube Sampling (LHS) to perform random model explorations for experiment design. In this
analysis, set ``<AnalysisType>LHS</AnalysisType>``. For example, The following input will utilize LHS to
generate ``10`` random LHS samples of input variables ``x, y`` with associated
``Uniform`` distributions, respectively.

.. code:: xml

  <?xml version="1.0" ?>
  <Simulation>
    <RunInfo>
      <WorkingDir>LHS_mishra</WorkingDir>
      <batchSize>1</batchSize>
    </RunInfo>

    <GlobalSettings>
      <AnalysisType>LHS</AnalysisType>
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
      <ExternalModel ModuleToLoad="../../models/mishraBirdConstrained" name="mishra" subType="">
        <inputs>x, y</inputs>
        <outputs>z</outputs>
      </ExternalModel>
    </Models>

  </Simulation>

When a dynamic model is provided, the users need to set ``<pivot>`` and ``<dynamic>`` node in the
``<GlobalSettings>``. As illustrated in the following example.

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

In addition, the users can use ``inputGroup`` and ``outputGroup`` to represent input and output variable list.
As illustrated in above example ``<ExternalModel>`` node.

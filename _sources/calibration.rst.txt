.. _cal:

Model Calibration
=================
Model calibrations via Bayesian inference to integrate experiments to improve model performance:
In this analysis, set ``<AnalysisType>model_calibration</AnalysisType>``.
When a dynamic model is provided, the users need to set ``<pivot>`` and ``<dynamic>`` node in the
``<GlobalSettings>``. As illustrated in the following example.
In addition, the initial values for input variables can be provided via ``<InitialInputs>``.

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

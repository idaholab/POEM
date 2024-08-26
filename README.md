# POEM
## Platform of Optimal Experiment Management (POEM)

An optimal experimental design platform powered with automated machine learning to automatically guides the design of experiment to be evaluated. More information can be found at https://idaholab.github.io/POEM/

## How to build html?

```bash
  pip install sphinx sphinx_rtd_theme nbsphinx sphinx-copybutton sphinx-autoapi
  conda install pandoc
  cd doc
  make html
  cd build/html
  python3 -m http.server
```

open your brower to: http://localhost:8000

## Installation

```
conda create -n poem_libs python=3.10
conda activate poem_libs
pip install poem-ravenframework
```

## Git Clone Repository

```
git clone git@github.com:idaholab/POEM.git
```

## Test

```
cd POEM/tests
poem -i lhs_sampling.xml
```
or test without run
```
poem -i lhs_sampling.xml -nr
```
or
```
poem -i lhs_sampling.xml --norun
```

## Capabilities

- Material thermal property modeling
- Design parameter optimization with multiple objectives
- Determining where to obtain new data in order to build accurate surrogate model
- Dynamic sensitivity and uncertainty analysis
- Model calibration through Bayesian inference
- Data adjustment through generalized linear least square method
- Machine learning aided parameter space exploration
- Bayesian optimization for optimal experimental design
- Pareto Frontier to guide the design of experiment to be evaluated
- Sparse grid stochastic collocation to accelerate experimental design

## Accelerate Experimental Design via Sparse Grid Stochastic Collocation Method

### Matyas Function

![image](https://media.github.inl.gov/user/161/files/f20d06cd-e81e-444c-bd6b-4ee09563e49a)

### Himmelblau's Function
![image](https://media.github.inl.gov/user/161/files/19151f05-b46e-4cbb-b1df-ed117629bf34)

### Pareto Frontier

![image](https://media.github.inl.gov/user/161/files/db838b94-18e8-47e5-b385-6d81cc2919bc)


## Accelerate Experimental Design via Bayesian Optimization Method

### Matyas Function
- LHS pre-samplings to simulate experiments
![LHS_sampling_scatter](https://media.github.inl.gov/user/161/files/eb50562d-a312-454b-ad58-f048c24614f2)
- Train Gaussian Process model with LHS samples, and use Grid approach to sample the trained Gaussian Process model
![Grid_rom_sampling_scatter](https://media.github.inl.gov/user/161/files/9648983f-625e-4260-9abf-63bb4a66e284)
- Utilize Bayesian Optimization with pre-trained Gaussian Process model to optimize the experimental design

<div align="center">
  <img src="https://media.github.inl.gov/user/161/files/0feaea6b-f5ec-45cb-8afb-0afb5c0653c9"><br><br>
  <img src="https://media.github.inl.gov/user/161/files/64381289-0bd7-4ef0-9810-83423728b640"><br><br>
</div>

https://media.github.inl.gov/user/161/files/9021d2e6-b6b0-4c8f-96e0-3d0005f03cd4

### Mishra

Bird Constrained Function

- LHS pre-samplings to simulate experiments
![LHS_sampling_scatter](https://media.github.inl.gov/user/161/files/427e246a-6cfc-4cdc-bf69-1e048b20c365)
- Train Gaussian Process model with LHS samples, and use Grid approach to sample the trained Gaussian Process model
![Grid_rom_sampling_scatter](https://media.github.inl.gov/user/161/files/21033f59-8d70-4666-afde-bdb8fe2e6a62)
- Utilize Bayesian Optimization with pre-trained Gaussian Process model to optimize the experimental design

<div align="center">
  <img src="https://media.github.inl.gov/user/161/files/b20666c9-14ad-4375-9ec5-9fed200eab81"><br><br>
  <img src="https://media.github.inl.gov/user/161/files/6b68bab0-125b-4813-b0c2-281b7478685e"><br><br>
</div>

https://media.github.inl.gov/user/161/files/86dc8928-7017-4a4b-893c-f77286ded0d4

## Dynamic Sensitivity Analysis

- Regression based method
- Sobol index based method

![sen](https://media.github.inl.gov/user/161/files/74d63142-ffe8-49dd-89c3-52d65d8841e0)

## Bayesian Model Calibration

### Analytic High-Dimensional Problem
A python analytic problem with 50 responses, three input parameters with uniform prior distributions.

![image](https://media.github.inl.gov/user/161/files/08ba5691-f4cc-49d8-9d1e-034ba14f40c2)



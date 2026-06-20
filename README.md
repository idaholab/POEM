# POEM
## Platform of Optimal Experiment Management (POEM)

An optimal experimental design platform powered with automated machine learning to automatically guides the design of experiment to be evaluated. This tool generates RAVEN (https://github.com/idaholab/raven) input files. More information can be found at https://idaholab.github.io/POEM/

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

## Source Installation (Linux/macOS)

When installing from source in plugin layout, create a local `POEM` symlink before editable install:

```bash
ln -s ../POEM .
pip install -e .
```

Keep the `POEM` symlink (`POEM -> ../POEM`) in the repository root while using `poem` from a source editable install.
Do not commit this symlink to git.

Note: this workaround is for Linux/macOS and is not supported on Windows.

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

![Sparse grid sampling for the Matyas function](docs/pics/SparseGrid_sampling_matyas.png)

### Himmelblau's Function
![Sparse grid sampling for Himmelblau's function](docs/pics/SparseGrid_sampling_himmelblau.png)

### Pareto Frontier

![Pareto frontier scatter plot](docs/pics/plot_pp_scatter-scatter.png)


## Accelerate Experimental Design via Bayesian Optimization Method

### Matyas Function
- LHS pre-samplings to simulate experiments
![LHS sampling scatter for the Matyas function](docs/pics/bayopt_matyas_LHS_existing_data.png)
- Train Gaussian Process model with LHS samples, and use Grid approach to sample the trained Gaussian Process model
![Grid ROM sampling scatter for the Matyas function](docs/pics/bayopt_matyas_grid_rom_sampling.png)
- Utilize Bayesian Optimization with pre-trained Gaussian Process model to optimize the experimental design

<div align="center">
  <img src="docs/pics/bayopt_matyas_opt_path.png" alt="Bayesian optimization path for the Matyas function"><br><br>
  <img src="docs/pics/bayopt_matyas_input_opt_path.png" alt="Bayesian optimization input path for the Matyas function"><br><br>
</div>

[Bayesian optimization animation for the Matyas function](docs/pics/bayopt_matyas.mp4)

### Mishra

Bird Constrained Function

- LHS pre-samplings to simulate experiments
![LHS sampling scatter for the Mishra bird constrained function](docs/pics/bayopt_mishra_LHS_existing_data.png)
- Train Gaussian Process model with LHS samples, and use Grid approach to sample the trained Gaussian Process model
![Grid ROM sampling scatter for the Mishra bird constrained function](docs/pics/bayopt_mishra.png)
- Utilize Bayesian Optimization with pre-trained Gaussian Process model to optimize the experimental design

<div align="center">
  <img src="docs/pics/bayopt_mishra_opt_path.png" alt="Bayesian optimization path for the Mishra bird constrained function"><br><br>
  <img src="docs/pics/bayopt_mishra_input_opt_path.png" alt="Bayesian optimization input path for the Mishra bird constrained function"><br><br>
</div>

[Bayesian optimization animation for the Mishra bird constrained function](docs/pics/bayopt_mishra.mp4)

## Dynamic Sensitivity Analysis

- Regression based method
- Sobol index based method

![Dynamic sensitivity analysis](docs/pics/sen.png)

## Bayesian Model Calibration

### Analytic High-Dimensional Problem
A python analytic problem with 50 responses, three input parameters with uniform prior distributions.

![Bayesian model calibration](docs/pics/model_calibration.png)

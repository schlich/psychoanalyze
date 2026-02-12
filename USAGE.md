# Psychoanalyze Simulate Module

## Overview

The `psychoanalyze.simulate` module provides functionality for generating prior predictive samples for psychometric data simulation using PyMC.

## Installation

```bash
pip install -e .
```

For testing:
```bash
pip install -e ".[test]"
```

For dashboard:
```bash
pip install -e ".[dashboard]"
```

## Usage

### Basic Usage

```python
from psychoanalyze import simulate

# Use all defaults
idata = simulate.run_prior_predictive()
```

### With Custom Parameters

```python
from psychoanalyze import simulate

# Specify draws and random seed for reproducibility
idata = simulate.run_prior_predictive(draws=1000, random_seed=42)
```

### With Custom Prior

```python
from psychoanalyze import simulate

# Define custom prior distributions
prior = simulate.LogisticPrior(
    x0_mu=0.6,      # Mean of midpoint
    x0_sigma=0.15,  # Std dev of midpoint
    k_mu=8.0,       # Mean of steepness
    k_sigma=2.5,    # Std dev of steepness
)

idata = simulate.run_prior_predictive(
    n_blocks=2,
    n_trials_per_block=100,
    logistic_prior=prior,
    draws=500,
    random_seed=123,
)
```

## API Reference

### `run_prior_predictive`

```python
def run_prior_predictive(
    n_blocks: int = 1,
    n_trials_per_block: int = 50,
    logistic_prior: LogisticPrior | None = None,
    *,
    draws: int = 500,
    random_seed: int | None = None,
) -> pm.backends.arviz.InferenceData
```

Generate prior predictive samples for psychometric data simulation.

**Parameters:**

- `n_blocks` (int, default=1): Number of blocks to simulate
- `n_trials_per_block` (int, default=50): Number of trials per block
- `logistic_prior` (LogisticPrior | None, default=None): Prior distribution parameters. If None, uses default values.
- `draws` (int, default=500): Number of prior predictive draws to generate (keyword-only)
- `random_seed` (int | None, default=None): Random seed for reproducibility (keyword-only)

**Returns:**

- `InferenceData`: ArviZ InferenceData object containing:
  - `prior`: Prior samples for x0 (midpoint) and k (steepness) parameters
  - `prior_predictive`: Simulated binary observations

### `LogisticPrior`

```python
@dataclass
class LogisticPrior:
    x0_mu: float = 0.5
    x0_sigma: float = 0.2
    k_mu: float = 5.0
    k_sigma: float = 2.0
```

Prior distribution parameters for the logistic psychometric function.

**Attributes:**

- `x0_mu`: Mean of the midpoint (x0) prior distribution
- `x0_sigma`: Standard deviation of the midpoint (x0) prior distribution
- `k_mu`: Mean of the steepness (k) prior distribution  
- `k_sigma`: Standard deviation of the steepness (k) prior distribution

## Model Details

The function implements a logistic psychometric model:

1. **Midpoint (x0)**: Sampled from a Normal distribution with mean `x0_mu` and std dev `x0_sigma`
2. **Steepness (k)**: Sampled from a Truncated Normal distribution with mean `k_mu`, std dev `k_sigma`, and lower bound of 0 (ensures positive steepness)
3. **Stimulus intensities**: Linearly spaced from 0 to 1 across `n_blocks * n_trials_per_block` trials
4. **Response probability**: Computed using the logistic (sigmoid) function: `p = sigmoid(k * (x - x0))`
5. **Observations**: Sampled from a Bernoulli distribution with probability `p`

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Or if using pixi:

```bash
pixi run pytest
```

## Dashboard

Launch the Marimo dashboard:

```bash
marimo edit nbs/simulate.py
```

The dashboard provides an interactive interface for exploring prior predictive samples with adjustable parameters.

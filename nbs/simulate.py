"""Marimo dashboard for psychometric data simulation.

This dashboard demonstrates the usage of the psychoanalyze.simulate module
for prior predictive sampling of psychometric functions.
"""

import marimo as mo
import psychoanalyze as psy


# Create UI sliders for parameters
n_blocks = mo.ui.slider(1, 10, value=1, label="Number of blocks")
n_trials_per_block = mo.ui.slider(10, 200, value=50, label="Trials per block")

# Create logistic prior with default values
logistic_prior = psy.simulate.LogisticPrior(
    x0_mu=0.5,
    x0_sigma=0.2,
    k_mu=5.0,
    k_sigma=2.0,
)

# Generate prior predictive samples using the dashboard pattern
# This is the critical API call that must not break
prior_samples = psy.simulate.run_prior_predictive(
    n_blocks=int(n_blocks.value),
    n_trials_per_block=int(n_trials_per_block.value),
    logistic_prior=logistic_prior,
)

# Display the results
mo.md(f"""
# Psychometric Simulation Dashboard

## Parameters
- Blocks: {n_blocks.value}
- Trials per block: {n_trials_per_block.value}
- Total trials: {n_blocks.value * n_trials_per_block.value}

## Prior Samples
- Draws: {prior_samples.prior.sizes['draw']}
- Variables: {list(prior_samples.prior.data_vars)}

## Prior Predictive
- Observations: {prior_samples.prior_predictive['obs'].shape}
""")

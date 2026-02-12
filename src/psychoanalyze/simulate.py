"""Simulation module for psychometric data generation."""

from dataclasses import dataclass

import numpy as np
import pymc as pm


@dataclass
class LogisticPrior:
    """Prior distribution parameters for logistic function.
    
    Attributes:
        x0_mu: Mean of the midpoint (x0) prior distribution
        x0_sigma: Standard deviation of the midpoint (x0) prior distribution
        k_mu: Mean of the steepness (k) prior distribution  
        k_sigma: Standard deviation of the steepness (k) prior distribution
    """
    x0_mu: float = 0.5
    x0_sigma: float = 0.2
    k_mu: float = 5.0
    k_sigma: float = 2.0


def run_prior_predictive(
    n_blocks: int = 1,
    n_trials_per_block: int = 50,
    logistic_prior: LogisticPrior | None = None,
    *,
    draws: int = 500,
    random_seed: int | None = None,
) -> pm.backends.arviz.InferenceData:
    """Run prior predictive sampling for psychometric data simulation.
    
    This function generates prior predictive samples for a logistic psychometric
    function with parameters x0 (midpoint) and k (steepness).
    
    Args:
        n_blocks: Number of blocks to simulate (default: 1)
        n_trials_per_block: Number of trials per block (default: 50)
        logistic_prior: Prior distribution parameters for the logistic function.
                       If None, uses default LogisticPrior values.
        draws: Number of prior predictive draws to generate (default: 500)
        random_seed: Random seed for reproducibility (default: None)
    
    Returns:
        InferenceData object containing:
            - prior: Prior samples for x0 and k parameters
            - prior_predictive: Simulated observations
    
    Examples:
        >>> # Use default parameters
        >>> idata = run_prior_predictive()
        
        >>> # Specify draws and random seed
        >>> idata = run_prior_predictive(draws=20, random_seed=42)
        
        >>> # Specify all parameters
        >>> prior = LogisticPrior(x0_mu=0.4, x0_sigma=0.1, k_mu=10.0, k_sigma=3.0)
        >>> idata = run_prior_predictive(
        ...     n_blocks=2,
        ...     n_trials_per_block=100,
        ...     logistic_prior=prior,
        ...     draws=1000,
        ...     random_seed=123,
        ... )
    """
    if logistic_prior is None:
        logistic_prior = LogisticPrior()
    
    n_trials = n_blocks * n_trials_per_block
    
    with pm.Model() as model:
        # Prior for midpoint (x0)
        x0 = pm.Normal("x0", mu=logistic_prior.x0_mu, sigma=logistic_prior.x0_sigma)
        
        # Prior for steepness (k) - must be positive
        k = pm.HalfNormal("k", sigma=logistic_prior.k_sigma)
        
        # Generate stimulus intensities
        x = np.linspace(0, 1, n_trials)
        
        # Logistic function for probability
        p = pm.math.sigmoid(k * (x - x0))
        
        # Simulated observations
        obs = pm.Bernoulli("obs", p=p, shape=n_trials)
        
        # Sample from prior predictive distribution
        idata = pm.sample_prior_predictive(
            samples=draws,
            random_seed=random_seed,
        )
    
    return idata

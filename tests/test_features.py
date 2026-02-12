"""Tests for psychoanalyze simulate module features."""

import numpy as np
import pytest

from psychoanalyze import simulate


class TestDataGenerationSimulation:
    """Test suite for data generation and simulation features."""
    
    def test_run_prior_predictive_sampling_with_default_draws(self):
        """Test that run_prior_predictive works with default draws parameter."""
        idata = simulate.run_prior_predictive(random_seed=42)
        
        # Check that prior group exists and has draw dimension
        assert "prior" in idata.groups()
        assert "draw" in idata.prior.dims
        
        # Check that default draws is 500
        assert idata.prior.sizes["draw"] == 500
        
        # Check that x0 and k variables exist in prior
        assert "x0" in idata.prior.data_vars
        assert "k" in idata.prior.data_vars
        
        # Check that prior_predictive group exists with obs variable
        assert "prior_predictive" in idata.groups()
        assert "obs" in idata.prior_predictive.data_vars
    
    def test_run_prior_predictive_with_specified_draws(self):
        """Test that run_prior_predictive respects specified draws parameter."""
        draws = 20
        idata = simulate.run_prior_predictive(draws=draws, random_seed=42)
        
        # Check that prior group has correct number of draws
        assert "prior" in idata.groups()
        assert idata.prior.sizes["draw"] == draws
        
        # Check that x0 and k variables exist
        assert "x0" in idata.prior.data_vars
        assert "k" in idata.prior.data_vars
        
        # Check that prior_predictive group exists
        assert "prior_predictive" in idata.groups()
        assert "obs" in idata.prior_predictive.data_vars
    
    def test_prior_predictive_curves_bounded(self):
        """Test that prior predictive samples have valid parameter bounds."""
        idata = simulate.run_prior_predictive(draws=100, random_seed=42)
        
        # Extract x0 and k values
        x0_values = idata.prior["x0"].values
        k_values = idata.prior["k"].values
        
        # All x0 values should be finite
        assert np.all(np.isfinite(x0_values)), "All x0 values should be finite"
        
        # All k values should be positive (TruncatedNormal with lower=0 ensures this)
        assert np.all(k_values > 0), "All k values should be positive"
        
        # Check that observations are binary (0 or 1)
        obs_values = idata.prior_predictive["obs"].values
        unique_values = np.unique(obs_values)
        assert np.all(np.isin(unique_values, [0, 1])), "Observations should be binary (0 or 1)"
    
    def test_run_prior_predictive_with_no_arguments(self):
        """Test that run_prior_predictive works with no arguments at all."""
        # This should use all defaults: n_blocks=1, n_trials_per_block=50, 
        # logistic_prior=None (uses default), draws=500, random_seed=None
        idata = simulate.run_prior_predictive()
        
        # Check basic structure
        assert "prior" in idata.groups()
        assert "prior_predictive" in idata.groups()
        
        # Check that we get the default 500 draws
        assert idata.prior.sizes["draw"] == 500
        
        # Check that variables exist
        assert "x0" in idata.prior.data_vars
        assert "k" in idata.prior.data_vars
        assert "obs" in idata.prior_predictive.data_vars
        
        # Check that obs has shape corresponding to n_blocks * n_trials_per_block = 1 * 50 = 50
        obs_shape = idata.prior_predictive["obs"].shape
        # Shape should be (draws, n_trials) = (500, 50)
        assert obs_shape == (500, 50), f"Expected shape (500, 50), got {obs_shape}"
    
    def test_dashboard_usage_pattern(self):
        """Test the usage pattern from the Marimo dashboard."""
        # Simulate dashboard calling pattern
        prior = simulate.LogisticPrior(
            x0_mu=0.6,
            x0_sigma=0.15,
            k_mu=8.0,
            k_sigma=2.5,
        )
        
        idata = simulate.run_prior_predictive(
            n_blocks=2,
            n_trials_per_block=75,
            logistic_prior=prior,
        )
        
        # Check that the call succeeded
        assert "prior" in idata.groups()
        assert "prior_predictive" in idata.groups()
        
        # Check that obs has correct shape: 2 blocks * 75 trials = 150
        obs_shape = idata.prior_predictive["obs"].shape
        # Shape should be (draws, n_trials) where draws uses default of 500
        assert obs_shape == (500, 150), f"Expected shape (500, 150), got {obs_shape}"

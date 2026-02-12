"""Core type definitions for psychoanalyze package."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class LinkFunction(Enum):
    """Link functions for psychometric functions.
    
    The psychometric function formula is: ψ(x) = γ + (1 - γ - λ) * F(x; x₀, k)
    where F is the link function.
    """
    LOGIT = "logit"
    WEIBULL = "weibull"
    GUMBEL = "gumbel"
    QUICK = "quick"


@dataclass
class BayesianFitSettings:
    """Settings for Bayesian fitting of psychometric functions.
    
    Attributes:
        draws: Number of samples to draw from the posterior distribution.
        chains: Number of parallel MCMC chains to run.
        random_seed: Random seed for reproducibility. None for random seed.
        link: Link function to use for the psychometric function.
    """
    draws: int
    chains: int
    random_seed: int | None
    link: LinkFunction


class CacheBackend(Enum):
    """Backend storage options for caching fit results."""
    MEMORY = "memory"
    DISK = "disk"


@dataclass
class FitArtifacts:
    """Results from fitting a psychometric function.
    
    Attributes:
        idata: InferenceData object containing MCMC samples and diagnostics.
               Typed as Any to avoid dependency on ArviZ at the type level.
               At runtime, this should be an arviz.InferenceData instance.
        threshold: Estimated threshold parameter (x₀).
        slope: Estimated slope parameter (k).
        intercept: Estimated intercept or lapse rate parameter.
    """
    idata: Any  # arviz.InferenceData - using Any to avoid import dependency
    threshold: float
    slope: float
    intercept: float

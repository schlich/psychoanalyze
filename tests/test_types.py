"""Tests for core type definitions."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from psychoanalyze.types import (
    BayesianFitSettings,
    CacheBackend,
    FitArtifacts,
    LinkFunction,
)


def test_link_function_enum():
    """Test that LinkFunction enum has required values."""
    assert hasattr(LinkFunction, "LOGIT")
    assert hasattr(LinkFunction, "WEIBULL")
    assert hasattr(LinkFunction, "GUMBEL")
    assert hasattr(LinkFunction, "QUICK")
    
    # Test that we can access the values
    assert LinkFunction.LOGIT.value == "logit"
    assert LinkFunction.WEIBULL.value == "weibull"
    assert LinkFunction.GUMBEL.value == "gumbel"
    assert LinkFunction.QUICK.value == "quick"


def test_cache_backend_enum():
    """Test that CacheBackend enum has required values."""
    assert hasattr(CacheBackend, "MEMORY")
    assert hasattr(CacheBackend, "DISK")
    
    assert CacheBackend.MEMORY.value == "memory"
    assert CacheBackend.DISK.value == "disk"


def test_bayesian_fit_settings_instantiation():
    """Test that BayesianFitSettings can be instantiated."""
    settings = BayesianFitSettings(
        draws=1000,
        chains=4,
        random_seed=42,
        link=LinkFunction.LOGIT
    )
    
    assert settings.draws == 1000
    assert settings.chains == 4
    assert settings.random_seed == 42
    assert settings.link == LinkFunction.LOGIT


def test_bayesian_fit_settings_with_none_seed():
    """Test that BayesianFitSettings accepts None for random_seed."""
    settings = BayesianFitSettings(
        draws=500,
        chains=2,
        random_seed=None,
        link=LinkFunction.WEIBULL
    )
    
    assert settings.random_seed is None


def test_fit_artifacts_instantiation():
    """Test that FitArtifacts can be instantiated."""
    artifacts = FitArtifacts(
        idata="mock_inference_data",  # Using string as mock for now
        threshold=0.5,
        slope=1.2,
        intercept=0.1
    )
    
    assert artifacts.idata == "mock_inference_data"
    assert artifacts.threshold == 0.5
    assert artifacts.slope == 1.2
    assert artifacts.intercept == 0.1


def test_import_from_psychoanalyze_types():
    """Test that types can be imported from psychoanalyze.types."""
    # This test validates the acceptance criteria:
    # "from psychoanalyze.types import BayesianFitSettings, CacheBackend, FitArtifacts, LinkFunction must not raise ImportError"
    try:
        from psychoanalyze.types import (
            BayesianFitSettings,
            CacheBackend,
            FitArtifacts,
            LinkFunction,
        )
        assert True  # Import succeeded
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_bayesian_module_imports():
    """Test that the bayesian module can import from types."""
    try:
        from psychoanalyze.analysis import bayesian
        assert hasattr(bayesian, "BayesianFitSettings")
        assert hasattr(bayesian, "CacheBackend")
        assert hasattr(bayesian, "FitArtifacts")
        assert hasattr(bayesian, "LinkFunction")
    except ImportError as e:
        pytest.fail(f"Import from bayesian module failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

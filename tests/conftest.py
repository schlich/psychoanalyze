import pytest
from tdda.referencetest import referencepytest, tag


def pytest_addoption(parser):
    referencepytest.addoption(parser)


def pytest_collection_modifyitems(session, config, items):
    referencepytest.tagged(config, items)


@pytest.fixture(scope="module")
def ref(request):
    return referencepytest.ref(request)


referencepytest.set_default_data_location("testdata")

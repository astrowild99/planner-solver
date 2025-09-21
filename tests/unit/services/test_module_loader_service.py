from unittest.mock import patch, MagicMock

import pytest
import pathlib

from planner_solver.config.models import ModuleConfig
from planner_solver.containers.singletons import types_service
from planner_solver.services.module_loader_service import ModuleLoaderService

@pytest.fixture
def mock_module_config():
    config = MagicMock(spec=ModuleConfig)
    # I use the current file as base to head to the modules
    filepath = str(pathlib.Path(__file__).parent)

    config.module_paths = [filepath + '/../../../src/base_module']
    return config

def test_load_base_module(mock_module_config):
    """
    smoke test on module loading behavior
    """
    loader_service = ModuleLoaderService(
        config=mock_module_config
    )

    loader_service.load_all()

    assert len(loader_service.loaded_modules) >= 3
    assert types_service.count() >= 3

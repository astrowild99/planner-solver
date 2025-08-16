from unittest.mock import patch, MagicMock

import pytest

from planner_solver.config.models import ModuleConfig
from planner_solver.services.module_loader_service import ModuleLoaderService

@pytest.fixture
def mock_module_config():
    config = MagicMock(spec=ModuleConfig)
    config.module_paths = ['./../src/base_module']
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
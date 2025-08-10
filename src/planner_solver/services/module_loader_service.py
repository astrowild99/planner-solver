import logging

from planner_solver.config.models import ModuleConfig
import os
import sys
import importlib
import importlib.util
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ModuleLoaderService:
    """
    a singleton to load all the modules available
    """
    def __init__(self, config: ModuleConfig):
        self.__config = config
        self.loaded_modules: Dict[str, Any] = {}
        logger.info("[Module Loader] - service loaded")

    def load_all(self):
        """
        Load all Python modules from the configured module paths.

        This method:
        1. Iterates through all configured module paths
        2. Converts relative paths to absolute paths
        3. Validates that paths exist
        4. Discovers and loads all Python modules in each path
        5. Handles import errors gracefully
        """
        paths: List[str] = self.__config.module_paths

        for path in paths:
            # Convert relative paths to absolute paths
            if not path.startswith('/'):
                cwd = os.getcwd()
                _path = os.path.join(cwd, path)
            else:
                _path = path

            # Validate path exists
            if not os.path.exists(_path):
                raise FileNotFoundError(f"Module path not found: {_path}")

            # Load all modules from this path
            self._load_modules_from_path(_path)

    def _load_modules_from_path(self, module_path: str):
        """
        Load all Python modules from a specific directory path.

        Args:
            module_path (str): The directory path containing Python modules
        """
        print(f"Loading modules from: {module_path}")

        # Add the path to sys.path if not already present
        if module_path not in sys.path:
            sys.path.insert(0, module_path)

        # Walk through the directory and find all Python files
        for root, dirs, files in os.walk(module_path):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    module_file_path = os.path.join(root, file)
                    self._load_single_module(module_file_path, module_path)

    def _load_single_module(self, module_file_path: str, base_path: str):
        """
        Load a single Python module from its file path.

        Args:
            module_file_path (str): Full path to the module file
            base_path (str): Base path for calculating module name
        """
        try:
            # Calculate module name from file path
            relative_path = os.path.relpath(module_file_path, base_path)
            module_name = relative_path.replace(os.sep, '.').replace('.py', '')

            # Skip if already loaded
            if module_name in self.loaded_modules:
                print(f"Module {module_name} already loaded, skipping...")
                return

            # Create module spec and load the module
            spec = importlib.util.spec_from_file_location(module_name, module_file_path)
            if spec is None:
                print(f"Could not create spec for module: {module_file_path}")
                return

            module = importlib.util.module_from_spec(spec)

            # Execute the module
            spec.loader.exec_module(module)

            # Store the loaded module
            self.loaded_modules[module_name] = module

            print(f"Successfully loaded module: {module_name}")

            # Call module initialization if it has an init function
            if hasattr(module, 'initialize'):
                try:
                    module.initialize()
                    print(f"Initialized module: {module_name}")
                except Exception as e:
                    print(f"Error initializing module {module_name}: {e}")

        except Exception as e:
            print(f"Error loading module {module_file_path}: {e}")

    def get_loaded_module(self, module_name: str):
        """
        Get a specific loaded module by name.

        Args:
            module_name (str): Name of the module to retrieve

        Returns:
            The loaded module or None if not found
        """
        return self.loaded_modules.get(module_name)

    def get_all_loaded_modules(self) -> Dict[str, Any]:
        """
        Get all loaded modules.

        Returns:
            Dictionary of all loaded modules
        """
        return self.loaded_modules.copy()

    def reload_module(self, module_name: str):
        """
        Reload a specific module (useful for development).

        Args:
            module_name (str): Name of the module to reload
        """
        if module_name in self.loaded_modules:
            try:
                importlib.reload(self.loaded_modules[module_name])
                print(f"Reloaded module: {module_name}")
            except Exception as e:
                print(f"Error reloading module {module_name}: {e}")
        else:
            print(f"Module {module_name} not found in loaded modules")

    def unload_module(self, module_name: str):
        """
        Unload a specific module.

        Args:
            module_name (str): Name of the module to unload
        """
        if module_name in self.loaded_modules:
            # Call cleanup function if it exists
            module = self.loaded_modules[module_name]
            if hasattr(module, 'cleanup'):
                try:
                    module.cleanup()
                    print(f"Cleaned up module: {module_name}")
                except Exception as e:
                    print(f"Error cleaning up module {module_name}: {e}")

            # Remove from loaded modules
            del self.loaded_modules[module_name]
            print(f"Unloaded module: {module_name}")
        else:
            print(f"Module {module_name} not found in loaded modules")
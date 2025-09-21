import os
import pytest

# Only enable debugging in Docker test environment
if os.getenv('ENABLE_DEBUG', 'false').lower() == 'true':
    try:
        import pydevd_pycharm

        # Try different host options for Docker networking
        hosts_to_try = [
            'host.docker.internal',  # Docker Desktop
            '172.17.0.1',           # Default Docker bridge
        ]

        debug_port = int(os.getenv('DEBUG_PORT', '5678'))
        connected = False

        for host in hosts_to_try:
            try:
                print(f"Trying to connect to PyCharm debugger at {host}:{debug_port}")
                pydevd_pycharm.settrace(host, port=debug_port)
                print(f"PyCharm debugger connected to {host}:{debug_port}!")
                connected = True
                break
            except Exception as e:
                print(f"Could not connect to {host}:{debug_port}: {e}")
                continue

        if not connected:
            print("Could not connect to PyCharm debugger on any host")

    except Exception as e:
        print(f"Could not setup PyCharm debugger: {e}")

@pytest.fixture(scope="session", autouse=True)
def setup_debug_environment():
    """Auto-executed fixture that sets up debugging for all tests"""
    # This fixture runs automatically for all tests
    # The debugger connection is already established above
    yield
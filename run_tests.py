"""
Run pytest tests for my-rxer Python components.
"""
import subprocess
import sys
import os
from pathlib import Path

# Change to project root
project_root = Path(__file__).parent
os.chdir(project_root)

# Add src to path for imports
sys.path.insert(0, str(project_root / "src"))


def run_pytest_tests():
    """Run pytest on core modules."""
    # Run pytest on test files in tests/
    result = subprocess.run([
        "python3", "-m", "pytest", "tests/", "-v", "--tb=short"
    ], capture_output=True, text=True)

    return result


def main():
    """Entry point."""
    result = run_pytest_tests()
    print(result.stdout)
    print(result.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
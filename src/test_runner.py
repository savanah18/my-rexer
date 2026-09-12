"""
Test runner for my-rxer Python tests.

Initialize the test suite and run all test files.
"""
import sys
import os
import unittest
from pathlib import Path

# Add src to path for imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir / '..' / '..'))

# Change to project root
os.chdir(str(src_dir / '..' / '..'))

def run_tests():
    """Discover and run all tests."""
    # Create test suite from all Python test files in tests/
    test_dir = Path(__file__).parent / "tests"
    
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    for test_file in sorted(test_dir.glob("test_*.py")):
        print(f"Loading: {test_file.stem}")
        
        # Import the test module
        module = __import__(f"tests.test_{test_file.stem}", fromlist=[""])
        
        # Get all test cases from the module
        module_tests = test_loader.loadTestsFromModule(module)
        test_suite.addTests(module_tests)
    
    # Create test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run tests
    result = runner.run(test_suite)
    
    return result

if __name__ == "__main__":
    result = run_tests()
    
    # Exit with error code if any tests failed
    sys.exit(0 if result.wasSuccessful() else 1)

#!/usr/bin/env python3
"""
Test runner for AI Document Analysis Application
Executes unit tests and integration tests
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_tests():
    """Run all tests and return exit code"""
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        src_dir = script_dir.parent
        
        # Set PYTHONPATH to include src directory
        env = os.environ.copy()
        env['PYTHONPATH'] = str(src_dir)
        
        logger.info("🧪 Starting AI Document Analysis Application Tests")
        logger.info(f"📁 Test directory: {script_dir}")
        logger.info(f"📁 Source directory: {src_dir}")
        
        # Change to the tests directory
        os.chdir(script_dir)
        
        # Run pytest with verbose output and coverage
        cmd = [
            sys.executable, '-m', 'pytest',
            '-v',                    # Verbose output
            '--tb=short',           # Short traceback format
            '--strict-markers',     # Strict marker handling
            '--disable-warnings',   # Disable warnings for cleaner output
            '.',                    # Run all tests in current directory
        ]
        
        logger.info(f"🚀 Running command: {' '.join(cmd)}")
        
        # Execute tests
        result = subprocess.run(cmd, env=env, capture_output=False)
        
        if result.returncode == 0:
            logger.info("✅ All tests passed successfully!")
        else:
            logger.error(f"❌ Tests failed with exit code: {result.returncode}")
            
        return result.returncode
        
    except Exception as e:
        logger.error(f"💥 Error running tests: {e}")
        return 1

def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("AI Document Analysis Application - Test Suite")
    logger.info("=" * 60)
    
    exit_code = run_tests()
    
    logger.info("=" * 60)
    if exit_code == 0:
        logger.info("🎉 Test execution completed successfully!")
    else:
        logger.info("💔 Test execution failed!")
    logger.info("=" * 60)
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 
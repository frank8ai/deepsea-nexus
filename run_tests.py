#!/usr/bin/env python3
"""
Deep-Sea Nexus v3.0 Test Runner

Run all tests for the hot-pluggable architecture.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            env={
                **os.environ,
                # Ensure subprocess uses the same Python environment when invoked
                "PYTHONNOUSERSITE": os.environ.get("PYTHONNOUSERSITE", "1"),
            },
        )
        
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"   ❌ Failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def run_python_tests():
    """Run Python unit and integration tests"""
    tests_dir = Path(__file__).parent / "tests"
    
    print("\n🧪 Running Python Tests...")
    
    # Test file paths
    test_files = [
        tests_dir / "test_units.py",
        tests_dir / "test_integration.py", 
        tests_dir / "test_performance.py",
        tests_dir / "brain" / "test_brain_units.py",
        tests_dir / "brain" / "test_brain_integration.py",
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if test_file.exists():
            print(f"\n📋 Running {test_file.name}...")
            py = sys.executable
            cmd = f"{py} {test_file} -v"
            success = run_command(cmd, f"Running {test_file.name}")
            all_passed = all_passed and success
        else:
            print(f"\n⚠️  Warning: {test_file} not found")
    
    return all_passed


def check_code_quality():
    """Check code quality (basic checks)"""
    print("\n🧹 Checking Code Quality...")
    
    # Check imports work
    try:
        import deepsea_nexus
        print("   ✅ Main import works")
        
        # Check key functions exist
        functions_to_check = [
            'create_app', 'nexus_init', 'nexus_recall', 'nexus_add',
            'get_plugin_registry', 'get_event_bus', 'CompressionManager'
        ]
        
        for func in functions_to_check:
            if hasattr(deepsea_nexus, func):
                print(f"   ✅ {func} available")
            else:
                print(f"   ❌ {func} missing")
                return False
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False


def validate_architecture():
    """Validate the hot-pluggable architecture"""
    print("\n🏗️  Validating Architecture...")
    
    try:
        import deepsea_nexus
        
        # Test app creation
        app = deepsea_nexus.create_app()
        print("   ✅ App creation works")
        
        # Test component access
        components = [
            ('get_plugin_registry', deepsea_nexus.get_plugin_registry()),
            ('get_event_bus', deepsea_nexus.get_event_bus()),
            ('get_config_manager', deepsea_nexus.get_config_manager()),
        ]
        
        for name, comp in components:
            if comp is not None:
                print(f"   ✅ {name} available")
            else:
                print(f"   ❌ {name} not available")
                return False
        
        # Test compression manager
        cm = deepsea_nexus.CompressionManager("gzip")
        test_data = b"test data"
        compressed = cm.compress(test_data)
        decompressed = cm.decompress(compressed)
        if decompressed == test_data:
            print("   ✅ Compression manager works")
        else:
            print("   ❌ Compression manager failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Architecture validation failed: {e}")
        return False


def main():
    """Main test runner"""
    print("🚀 Deep-Sea Nexus v3.0 Test Suite")
    print("=" * 50)
    
    # Change to the skills directory
    skills_dir = Path(__file__).parent
    os.chdir(skills_dir)

    # Ensure the workspace `skills/` directory is importable.
    workspace_skills_dir = str(skills_dir.parent)
    if workspace_skills_dir not in sys.path:
        sys.path.insert(0, workspace_skills_dir)

    # Ensure tests can import `deepsea_nexus` even when executed as subprocesses.
    # (The project directory is `deepsea-nexus` but the import name is `deepsea_nexus`.)
    os.environ["PYTHONPATH"] = workspace_skills_dir + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else "")
    
    all_passed = True
    
    # Run architecture validation
    all_passed = validate_architecture() and all_passed
    
    # Run code quality checks
    all_passed = check_code_quality() and all_passed
    
    # Run Python tests
    all_passed = run_python_tests() and all_passed
    
    # Final summary
    print("\n" + "=" * 50)
    print("📋 TEST RUNNER SUMMARY")
    print("=" * 50)
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("   ✓ Architecture validation: PASS")
        print("   ✓ Code quality: PASS") 
        print("   ✓ Python tests: RUN")
        print("\n🎉 Deep-Sea Nexus v3.0 is ready!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("   Check output above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Test script for file size feature in DirectoryTree.
Run this to verify the implementation works correctly.
"""

import os
import tempfile
import json
from dir_tree import DirectoryTree


def test_backward_compatibility():
    """Test that sizes are NOT shown by default (backward compatibility)."""
    print("🧪 Test 1: Backward Compatibility...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("x" * 1000)
        
        # Default: no sizes
        tree = DirectoryTree(root_dir=tmpdir)
        output = tree.to_json()
        
        assert "(KB)" not in output, "FAILED: Found KB in output when sizes should be disabled"
        assert "(B)" not in output, "FAILED: Found B in output when sizes should be disabled"
        
        print("   ✅ PASSED: No sizes shown by default")
        return True


def test_file_sizes_enabled():
    """Test that sizes appear when enabled."""
    print("\n🧪 Test 2: File Sizes Enabled...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files with known sizes
        small_file = os.path.join(tmpdir, "small.txt")
        with open(small_file, 'w') as f:
            f.write("x" * 100)  # 100 bytes
        
        medium_file = os.path.join(tmpdir, "medium.txt")
        with open(medium_file, 'w') as f:
            f.write("x" * 1536)  # 1.5 KB
        
        # Enable sizes
        tree = DirectoryTree(root_dir=tmpdir, show_file_sizes=True)
        output = tree.to_json()
        tree_data = json.loads(output)
        
        print(f"\n   Tree output:\n{tree_data['tree_print']}\n")
        
        assert "100.0 B" in output, "FAILED: Expected '100.0 B' in output"
        assert "1.5 KB" in output, "FAILED: Expected '1.5 KB' in output"
        
        print("   ✅ PASSED: File sizes displayed correctly")
        return True


def test_no_directory_sizes():
    """Test that directories don't get sizes."""
    print("\n🧪 Test 3: Directories Without Sizes...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create subdirectory
        subdir = os.path.join(tmpdir, "mydir")
        os.makedirs(subdir)
        
        # Create file in subdirectory
        test_file = os.path.join(subdir, "file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        tree = DirectoryTree(root_dir=tmpdir, show_file_sizes=True)
        output = tree.to_json()
        tree_data = json.loads(output)
        
        print(f"\n   Tree output:\n{tree_data['tree_print']}\n")
        
        # Directory should appear without size
        assert "mydir" in output, "FAILED: Directory name not found"
        # Check that there's no size immediately after directory name
        # (before the file inside it shows a size)
        lines = tree_data['tree_print'].split('\n')
        for line in lines:
            if 'mydir' in line and '(' in line:
                # Make sure it's not "mydir (" pattern
                if 'mydir/' in line or 'mydir' in line:
                    assert not line.strip().startswith('├── mydir (') and not line.strip().startswith('└── mydir ('), \
                        f"FAILED: Directory has size in line: {line}"
        
        print("   ✅ PASSED: Directories shown without sizes")
        return True


def test_size_formatting():
    """Test various file sizes format correctly."""
    print("\n🧪 Test 4: Size Formatting...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_cases = [
            ("100b.txt", 100, "100.0 B"),
            ("1kb.txt", 1024, "1.0 KB"),
            ("1.5kb.txt", 1536, "1.5 KB"),
            ("1mb.txt", 1048576, "1.0 MB"),
            ("5mb.txt", 5242880, "5.0 MB"),
        ]
        
        for filename, size, expected in test_cases:
            filepath = os.path.join(tmpdir, filename)
            with open(filepath, 'wb') as f:
                f.write(b'x' * size)
        
        tree = DirectoryTree(root_dir=tmpdir, show_file_sizes=True)
        output = tree.to_json()
        tree_data = json.loads(output)
        
        print(f"\n   Tree output:\n{tree_data['tree_print']}\n")
        
        for filename, size, expected in test_cases:
            assert expected in output, f"FAILED: Expected '{expected}' for {filename}"
            print(f"   ✅ Found: {expected}")
        
        print("   ✅ PASSED: All size formats correct")
        return True


def test_mixed_content():
    """Test with mixed files and directories."""
    print("\n🧪 Test 5: Mixed Content (Files + Directories)...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files
        file1 = os.path.join(tmpdir, "readme.txt")
        with open(file1, 'w') as f:
            f.write("x" * 2048)  # 2 KB
        
        file2 = os.path.join(tmpdir, "config.json")
        with open(file2, 'w') as f:
            f.write("x" * 856)  # 856 B
        
        # Create directory with file
        subdir = os.path.join(tmpdir, "utils")
        os.makedirs(subdir)
        
        file3 = os.path.join(subdir, "helper.py")
        with open(file3, 'w') as f:
            f.write("x" * 1100)  # ~1.1 KB
        
        tree = DirectoryTree(root_dir=tmpdir, show_file_sizes=True)
        output = tree.to_json()
        tree_data = json.loads(output)
        
        print(f"\n   Tree output:\n{tree_data['tree_print']}\n")
        
        # Check files have sizes
        assert "readme.txt (2.0 KB)" in output, "FAILED: readme.txt should have size"
        assert "856.0 B" in output, "FAILED: config.json should have size"
        assert "1.1 KB" in output or "1.0 KB" in output, "FAILED: helper.py should have size"
        
        print("   ✅ PASSED: Mixed content handled correctly")
        return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Testing File Size Feature Implementation")
    print("=" * 60)
    
    tests = [
        test_backward_compatibility,
        test_file_sizes_enabled,
        test_no_directory_sizes,
        test_size_formatting,
        test_mixed_content,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 All tests passed! Implementation is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

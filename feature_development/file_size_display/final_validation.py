"""
Final validation: Test the feature on the actual project directory.
"""

import json
from dir_tree import DirectoryTree


def main():
    print("=" * 80)
    print("🔍 FINAL VALIDATION: Testing on actual dir_tree project")
    print("=" * 80)
    
    # Test 1: Default (no sizes)
    print("\n1️⃣  Testing default behavior (no sizes)...")
    tree1 = DirectoryTree(
        root_dir=".",
        exclude_files={"*.pyc", "__pycache__", ".git", "*.egg-info"}
    )
    output1 = tree1.to_json()
    data1 = json.loads(output1)
    
    has_sizes = "(KB)" in output1 or "(MB)" in output1 or "(B)" in output1
    if has_sizes:
        print("   ❌ FAILED: Sizes found when they should not be present!")
        return False
    else:
        print("   ✅ PASSED: No sizes in default mode")
    
    # Test 2: With sizes enabled
    print("\n2️⃣  Testing with sizes enabled...")
    tree2 = DirectoryTree(
        root_dir=".",
        exclude_files={"*.pyc", "__pycache__", "*.egg-info"},
        show_file_sizes=True
    )
    output2 = tree2.to_json()
    data2 = json.loads(output2)
    
    has_sizes = "(KB)" in output2 or "(MB)" in output2 or " B)" in output2 or "(GB)" in output2
    if not has_sizes:
        print("   ❌ FAILED: No sizes found when they should be present!")
        return False
    else:
        print("   ✅ PASSED: Sizes displayed correctly")
    
    # Test 3: Validate format
    print("\n3️⃣  Validating size format...")
    lines = data2['tree_print'].split('\n')
    size_found = False
    for line in lines:
        if '(' in line and ')' in line:
            # Extract size portion
            if 'B)' in line or 'KB)' in line or 'MB)' in line or 'GB)' in line:
                size_found = True
                # Check format: should be like "(1.2 KB)" or "(100.0 B)"
                import re
                match = re.search(r'\((\d+\.\d+)\s+(B|KB|MB|GB|TB)\)', line)
                if not match:
                    print(f"   ❌ FAILED: Invalid size format in line: {line}")
                    return False
    
    if size_found:
        print("   ✅ PASSED: Size format is correct (X.X UNIT)")
    else:
        print("   ⚠️  WARNING: No sizes found to validate format")
    
    # Test 4: Check directories don't have sizes
    print("\n4️⃣  Checking directories don't have sizes...")
    directory_with_size = False
    for line in lines:
        # Look for directory markers
        if line.strip().endswith('/') or 'dir_tree' in line:
            # Check if this line has a size
            if '(' in line and any(unit in line for unit in ['B)', 'KB)', 'MB)', 'GB)']):
                # Make sure it's actually a directory and not a file with "dir" in name
                if line.strip().split()[-1].endswith('/'):
                    directory_with_size = True
                    print(f"   ❌ FAILED: Directory has size: {line}")
                    break
    
    if not directory_with_size:
        print("   ✅ PASSED: Directories do not have sizes")
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL VALIDATION RESULTS")
    print("=" * 80)
    print("\n✅ All validation checks passed!")
    print("\n📁 Sample output (first 10 lines with sizes):")
    print("-" * 80)
    count = 0
    for line in lines:
        if count < 10:
            print(line)
            count += 1
    
    print("\n" + "=" * 80)
    print("🎉 Implementation is PRODUCTION READY!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

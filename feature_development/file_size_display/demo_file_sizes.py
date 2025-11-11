"""
Demo script to show the file size feature in action.
"""

import os
import json
from dir_tree import DirectoryTree


def demo():
    """Demonstrate the file size feature."""
    print("=" * 70)
    print("📁 dir_tree File Size Feature Demo")
    print("=" * 70)
    
    # Demo 1: Without sizes (default)
    print("\n1️⃣  DEFAULT BEHAVIOR (show_file_sizes=False)")
    print("-" * 70)
    
    tree1 = DirectoryTree(root_dir=".", exclude_files={
        "*.pyc", "__pycache__", ".git", "*.egg-info", ".gitignore", 
        ".gptignore", "allfiles.txt"
    })
    output1 = tree1.to_json()
    data1 = json.loads(output1)
    print(data1['tree_print'])
    
    # Demo 2: With sizes enabled
    print("\n\n2️⃣  WITH FILE SIZES (show_file_sizes=True)")
    print("-" * 70)
    
    tree2 = DirectoryTree(root_dir=".", exclude_files={
        "*.pyc", "__pycache__", ".git", "*.egg-info", ".gitignore",
        ".gptignore", "allfiles.txt"
    }, show_file_sizes=True)
    output2 = tree2.to_json()
    data2 = json.loads(output2)
    print(data2['tree_print'])
    
    # Demo 3: Show JSON structure
    print("\n\n3️⃣  JSON OUTPUT SAMPLE")
    print("-" * 70)
    print("With sizes enabled, the tree_print field contains size info:")
    print(json.dumps(data2, indent=2)[:500] + "...")
    
    print("\n\n✅ Demo Complete!")
    print("=" * 70)
    print("\n📝 Key Points:")
    print("   • Default behavior unchanged (backward compatible)")
    print("   • Sizes shown only when show_file_sizes=True")
    print("   • Format: filename (X.X UNIT) where UNIT = B, KB, MB, GB, TB")
    print("   • Directories never show sizes")
    print("   • Symlinks show target size (not link size)")
    print("   • Graceful error handling (permission errors, broken links)")
    print("=" * 70)


if __name__ == "__main__":
    demo()

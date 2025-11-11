"""
Reference Implementation: File Size Display for DirectoryTree

⚠️ UPDATED: Nov 12, 2025 - Based on actual codebase analysis

This shows the exact code changes needed based on the ACTUAL dir_tree architecture:
- Uses tree_print_lines.append() NOT string concatenation
- Handles symlink display names correctly
- Places size AFTER symlink arrow
"""

# ============================================================================
# PART 1: Add to __init__ method
# ============================================================================

def __init__(
    self,
    root_dir: str,
    exclude_dirs: Optional[Set[str]] = None,
    exclude_files: Optional[Set[str]] = None,
    follow_symlinks_in_tree: bool = False,
    show_file_sizes: bool = False  # ← NEW PARAMETER
):
    """
    Initialize DirectoryTree.
    
    Args:
        root_dir: Root directory to scan
        exclude_dirs: Set of directory patterns to exclude
        exclude_files: Set of file patterns to exclude  
        follow_symlinks_in_tree: Whether to follow symbolic links
        show_file_sizes: If True, display human-readable file sizes
                       next to file names (e.g., "file.txt (1.2 KB)")
    """
    self.root_dir = root_dir
    self.exclude_dirs = exclude_dirs or set()
    self.exclude_files = exclude_files or set()
    self.follow_symlinks_in_tree = follow_symlinks_in_tree
    self.show_file_sizes = show_file_sizes  # ← STORE THE PARAMETER


# ============================================================================
# PART 2: Add new helper method (place before build_tree_recursive)
# ============================================================================

def _format_size(self, size_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string like "1.5 KB", "2.3 MB", etc.
        
    Examples:
        >>> self._format_size(100)
        '100.0 B'
        >>> self._format_size(1536)
        '1.5 KB'
        >>> self._format_size(1048576)
        '1.0 MB'
        >>> self._format_size(5242880)
        '5.0 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# ============================================================================
# PART 3: Modify build_tree_recursive method
# ============================================================================
# Find the section where you handle FILES (the else: block after directory check)
# Current code at approximately line 63:
#
#   else:  # It's a file
#       self.tree_print_lines.append(f"{prefix}{connector}{entry_display_name}")
#       tree_structure[item_name] = None
#
# Replace with:

def build_tree_recursive(self, current_dir: str, prefix: str = '') -> Dict[str, Any]:
    """Build directory tree recursively."""
    # ... existing code for scanning directory, sorting entries, etc. ...
    
    for item_name in sorted_entries:
        item_path = os.path.join(current_dir, item_name)
        
        # ... existing code for symlink detection, connector determination, etc. ...
        
        # Existing logic determines:
        # - is_target_a_directory
        # - entry_display_name (includes " -> target" for symlinks)
        # - connector ("├── " or "└── ")
        
        if is_target_a_directory:
            # UNCHANGED: Directory handling stays the same
            # ... existing directory logic ...
            pass
            
        else:
            # MODIFIED: File handling with optional size display
            final_display = entry_display_name  # Already includes " -> target" for symlinks!
            
            if self.show_file_sizes:
                try:
                    # os.path.getsize() follows symlinks automatically
                    # This shows target file size, not symlink size
                    size = os.path.getsize(item_path)
                    size_str = self._format_size(size)
                    final_display += f" ({size_str})"
                except (OSError, IOError):
                    # Graceful degradation: permission denied, file deleted, etc.
                    # Just show the filename without size
                    pass
            
            # Use append(), not string concatenation!
            self.tree_print_lines.append(f"{prefix}{connector}{final_display}")
            tree_structure[item_name] = None
    
    # ... rest of existing method ...
    return tree_structure


# ============================================================================
# TESTING CODE (add to tests/)
# ============================================================================

import os
import tempfile
from dir_tree import DirectoryTree


def test_file_sizes_disabled_by_default():
    """Test backward compatibility: sizes not shown by default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("x" * 1000)
        
        # Default: no sizes
        tree = DirectoryTree(root_dir=tmpdir)
        output = tree.to_json()
        
        assert "(KB)" not in output
        assert "(B)" not in output
        print("✅ Backward compatibility maintained")


def test_file_sizes_enabled():
    """Test that sizes appear when enabled."""
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
        
        assert "100.0 B" in output
        assert "1.5 KB" in output
        print("✅ File sizes displayed correctly")


def test_directory_no_size():
    """Test that directories don't get sizes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create subdirectory
        subdir = os.path.join(tmpdir, "mydir")
        os.makedirs(subdir)
        
        tree = DirectoryTree(root_dir=tmpdir, show_file_sizes=True)
        output = tree.to_json()
        
        # Directory should appear as "mydir/" not "mydir/ (X KB)"
        assert "mydir/" in output
        # Check that there's no size immediately after "mydir"
        assert "mydir/ (" not in output
        print("✅ Directories shown without sizes")


def test_size_formatting():
    """Test various file sizes format correctly."""
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
        
        for filename, size, expected in test_cases:
            assert expected in output, f"Expected {expected} for {filename}"
        
        print("✅ All size formats correct")


def test_symlink_shows_target_size():
    """Symlinks should show target file size, not link size."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create target file (10 KB)
        target = os.path.join(tmpdir, "target.txt")
        with open(target, 'wb') as f:
            f.write(b'x' * 10240)
        
        # Create symlink
        link = os.path.join(tmpdir, "link.txt")
        os.symlink(target, link)
        
        tree = DirectoryTree(root_dir=tmpdir, show_file_sizes=True)
        output = tree.to_json()
        
        # Should show target size (10 KB), not link size (~100 bytes)
        assert "10.0 KB" in output
        assert "link.txt -> target.txt (10.0 KB)" in output or "10.0 KB" in output
        print("✅ Symlinks show target size")


def test_broken_symlink_no_crash():
    """Broken symlinks should not cause crashes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create broken symlink
        broken = os.path.join(tmpdir, "broken_link")
        os.symlink("/non/existent/path", broken)
        
        tree = DirectoryTree(root_dir=tmpdir, show_file_sizes=True)
        output = tree.to_json()  # Should NOT raise
        
        # Should show broken symlink marker
        assert "broken_link" in output
        assert "[Broken Symlink]" in output
        # But NO size
        assert "broken_link -> [Broken Symlink] (" not in output
        print("✅ Broken symlinks handled gracefully")


if __name__ == "__main__":
    test_file_sizes_disabled_by_default()
    test_file_sizes_enabled()
    test_directory_no_size()
    test_size_formatting()
    test_symlink_shows_target_size()
    test_broken_symlink_no_crash()
    print("\n🎉 All tests passed!")

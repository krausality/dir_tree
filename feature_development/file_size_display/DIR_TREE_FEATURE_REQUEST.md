# Feature Request: File Size Display in DirectoryTree

## Summary
Add optional file size display in the tree output to show human-readable file sizes (B, KB, MB, GB, TB) next to file names.

## ⚠️ Implementation Note
This request has been reviewed against the actual `dir_tree` codebase. Key architectural differences from initial assumptions have been identified:

1. **Code Structure:** Uses `tree_print_lines.append()` (list) instead of string concatenation
2. **Entry Display:** Must handle symlink targets correctly: `"link -> target (size)"` not `"link (size) -> target"`
3. **Symlink Size:** Should show target size via `os.path.getsize()` (follows symlinks automatically)
4. **JSON Structure:** Sizes only appear in `tree_print`, not in nested `tree` dict

See implementation checklist for adjusted code snippets.

## Use Case
The `4gpt` project uses `dir_tree` to generate file structure overviews. We recently added file size display in the file content concatenation section and want to provide consistent size information in the tree view as well.

## Current Behavior

```
project/
├── main.py
├── config.json
└── utils/
    └── helper.py
```

## Desired Behavior

```
project/
├── main.py (2.3 KB)
├── config.json (856.0 B)
└── utils/
    └── helper.py (1.1 KB)
```

---

## API Requirements

### 1. Constructor Parameter

Add a new optional parameter `show_file_sizes` to the `DirectoryTree.__init__()` method:

```python
class DirectoryTree:
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
            show_file_sizes: If True, display file sizes in human-readable format
                           next to file names in the tree output (default: False)
        """
```

### 2. Backward Compatibility

**Critical:** The parameter must be **optional** with a **default value of `False`** to maintain backward compatibility with existing code.

```python
# Existing code should continue to work without changes
tree = DirectoryTree(root_dir=".", exclude_files={"*.pyc"})
# Output: No file sizes (current behavior)

# New code can opt-in to file sizes
tree = DirectoryTree(root_dir=".", exclude_files={"*.pyc"}, show_file_sizes=True)
# Output: Files show sizes
```

---

## Implementation Details

### File Size Formatting Function

Implement a helper method to convert bytes to human-readable format:

```python
def _format_size(self, size_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string like "1.5 KB", "2.3 MB", etc.
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
```

**Formatting Rules:**
- Always show **1 decimal place** (e.g., `12.0 B`, `1.5 KB`)
- Units: `B` → `KB` → `MB` → `GB` → `TB`
- Threshold: 1024.0 for each unit transition
- Examples:
  - `100` bytes → `"100.0 B"`
  - `1536` bytes → `"1.5 KB"`
  - `1048576` bytes → `"1.0 MB"`
  - `5242880` bytes → `"5.0 MB"`

### Tree Building Modification

Modify the tree building logic to conditionally include file sizes:

```python
def build_tree_recursive(self, current_dir: str, prefix: str = '') -> Dict[str, Any]:
    # ... existing logic ...
    
    for entry in entries:
        path = os.path.join(current_dir, entry)
        
        if os.path.isdir(path):
            # Directories: no size
            tree_str += f"{prefix}{connector}{entry}/\n"
        else:
            # Files: optionally add size
            if self.show_file_sizes:
                try:
                    size = os.path.getsize(path)
                    size_str = self._format_size(size)
                    tree_str += f"{prefix}{connector}{entry} ({size_str})\n"
                except (OSError, IOError):
                    # Fallback if size can't be determined
                    tree_str += f"{prefix}{connector}{entry}\n"
            else:
                tree_str += f"{prefix}{connector}{entry}\n"
```

### Error Handling

- If `os.path.getsize()` fails (permission denied, file deleted, etc.), silently fall back to showing the filename **without** size
- No exceptions should be raised to the caller
- Behavior should degrade gracefully

---

## JSON Output Integration

The `tree_print` field in the JSON output should reflect the file sizes when enabled:

```python
tree_data = {
    "root": "project",
    "tree": { ... },
    "tree_print": "project/\n├── main.py (2.3 KB)\n└── config.json (856.0 B)\n"
}
```

---

## Testing Requirements

### Test Cases

1. **Backward Compatibility Test:**
   ```python
   tree = DirectoryTree(root_dir="test_dir")
   assert "(KB)" not in tree.to_json()  # No sizes by default
   ```

2. **File Size Display Test:**
   ```python
   tree = DirectoryTree(root_dir="test_dir", show_file_sizes=True)
   json_output = tree.to_json()
   assert "(KB)" in json_output or "(B)" in json_output
   ```

3. **Size Format Test:**
   ```python
   # Create test files with known sizes
   # 100 bytes
   # 1536 bytes (1.5 KB)
   # 1048576 bytes (1.0 MB)
   tree = DirectoryTree(root_dir="test_dir", show_file_sizes=True)
   output = tree.to_json()
   assert "100.0 B" in output
   assert "1.5 KB" in output
   assert "1.0 MB" in output
   ```

4. **Error Handling Test:**
   ```python
   # Test with files that might cause permission errors
   # Should not raise exceptions
   tree = DirectoryTree(root_dir="test_dir", show_file_sizes=True)
   tree.to_json()  # Should complete successfully
   ```

5. **Directory Exclusion Test:**
   ```python
   # Sizes should only appear for files, not directories
   tree = DirectoryTree(root_dir="test_dir", show_file_sizes=True)
   output = tree.to_json()
   # Directories should not have sizes: "mydir/" not "mydir/ (123 KB)"
   ```

---

## Integration Example in 4gpt

Once implemented, we will use it like this:

```python
def generate_tree(self):
    tree = DirectoryTree(
        root_dir=self.root_dir,
        exclude_dirs=set(),
        exclude_files=self.exclude_patterns,
        follow_symlinks_in_tree=self.follow_symlinks,
        show_file_sizes=True  # ← Enable file sizes
    )
    try:
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("File Structure:\n")
            tree_json_str = tree.to_json()
            tree_data = json.loads(tree_json_str)
            f.write(tree_data["tree_print"])
            f.write("\n\n")
    except IOError as e:
        print(f"Error writing to output file {self.output_file}: {e}")
```

---

## Performance Considerations

- `os.path.getsize()` is a **single syscall** per file (O(1) operation)
- No significant performance impact expected
- For large directories (10,000+ files), overhead should be < 100ms
- File sizes are retrieved from filesystem metadata, not by reading file contents

---

## Documentation Updates Needed

1. Update `DirectoryTree` docstring with new parameter
2. Add example in README showing size display
3. Update CHANGELOG with new feature
4. Ensure type hints are accurate (`show_file_sizes: bool = False`)

---

## Version Compatibility

- Minimum Python version: **3.7+** (f-strings, type hints)
- No new external dependencies required
- Standard library only: `os`, `typing`

---

## Priority: Medium-High

This feature enhances user experience by providing file size context directly in the tree view, matching the functionality already present in file content headers in the `4gpt` project.

---

## Additional Notes

- Consider adding a configuration option for **custom size formatting** in future versions (e.g., always use KB, or use binary units like KiB)
- Consider adding **total directory size** in future versions (shown next to directory names)
- Current request focuses on **file-level sizes only** for simplicity

---

## Contact

For questions or clarifications, please reference this document when implementing.

**Related Project:** https://github.com/krausality/4gpt

# dir_tree Implementation Checklist

⚠️ **UPDATED:** Based on actual codebase analysis (Nov 12, 2025)

Quick reference for implementing file size display in the `dir_tree` package.

## ⚠️ Critical Architecture Notes

The actual `dir_tree` implementation differs from initial assumptions:

1. **Uses `tree_print_lines.append()`** - NOT string concatenation (`tree_str +=`)
2. **Complex symlink handling** - Size must be placed AFTER symlink target
3. **Entry display name** - Already includes `" -> target"` for symlinks
4. **`os.path.getsize()`** - Automatically follows symlinks (shows target size, not link size)

## ✅ Implementation Steps

### 1. Add Constructor Parameter
```python
def __init__(
    self,
    root_dir: str,
    exclude_dirs: Optional[Set[str]] = None,
    exclude_files: Optional[Set[str]] = None,
    follow_symlinks_in_tree: bool = False,
    show_file_sizes: bool = False  # ← ADD THIS
):
    self.root_dir = os.path.abspath(root_dir)
    self.explicit_exclude_dir_names = exclude_dirs if exclude_dirs is not None else set()
    self.general_exclude_patterns = exclude_files if exclude_files is not None else set()
    self.follow_symlinks_in_tree = follow_symlinks_in_tree
    self.show_file_sizes = show_file_sizes  # ← ADD THIS
    self.tree = {}
    self.tree_print_lines = []  # ← Note: Uses list, not string!
```

### 2. Add Size Formatter Method
```python
def _format_size(self, size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
```

### 3. Modify Tree Building (CORRECTED)

**Location:** In `build_tree_recursive()`, in the `else:` block for files (NOT directories)

**BEFORE (current code, approx line 63):**
```python
else:  # It's a file
    self.tree_print_lines.append(f"{prefix}{connector}{entry_display_name}")
    tree_structure[item_name] = None
```

**AFTER (with size support):**
```python
else:  # It's a file
    final_display = entry_display_name  # Already includes " -> target" for symlinks
    
    if self.show_file_sizes:
        try:
            # os.path.getsize() follows symlinks (shows target size)
            size = os.path.getsize(item_path)
            size_str = self._format_size(size)
            final_display += f" ({size_str})"
        except (OSError, IOError):
            # Graceful degradation: show without size on error
            pass
    
    self.tree_print_lines.append(f"{prefix}{connector}{final_display}")
    tree_structure[item_name] = None
```

**Important:** Size is appended AFTER `entry_display_name` which already contains symlink arrow if applicable.

## 🧪 Quick Test

```python
# Test backward compatibility (default: no sizes)
from dir_tree import DirectoryTree
tree1 = DirectoryTree(root_dir=".")
print(tree1.to_json())  # Should NOT show sizes

# Test new feature (opt-in)
tree2 = DirectoryTree(root_dir=".", show_file_sizes=True)
print(tree2.to_json())  # Should show sizes like "(1.2 KB)"
```

## 📊 Expected Output Format

**Without sizes (current/default):**
```
project/
├── main.py
└── config.json
```

**With sizes (when show_file_sizes=True):**
```
project/
├── main.py (2.3 KB)
└── config.json (856.0 B)
```

## 🔄 Integration in 4gpt

Once deployed, update `4gpt/forgpt/core.py`:

```python
def generate_tree(self):
    tree = DirectoryTree(
        root_dir=self.root_dir,
        exclude_dirs=set(),
        exclude_files=self.exclude_patterns,
        follow_symlinks_in_tree=self.follow_symlinks,
        show_file_sizes=True  # ← Simply add this
    )
    # ... rest stays the same
```

## 📋 Validation Checklist

- [ ] Default behavior unchanged (backward compatible)
- [ ] `show_file_sizes=True` adds sizes to files only
- [ ] Directories do NOT show sizes (including directory symlinks)
- [ ] Format: `filename (X.X UNIT)` OR `symlink -> target (X.X UNIT)`
- [ ] Units: B, KB, MB, GB, TB
- [ ] 1 decimal place always shown
- [ ] Graceful error handling (no exceptions on permission errors)
- [ ] Works with symlinks when `follow_symlinks_in_tree=True`
- [ ] JSON output includes sizes in `tree_print` field
- [ ] Symlink size shows TARGET size, not link size (via `os.path.getsize()`)
- [ ] Broken symlinks handled gracefully (no size shown)

## 🎯 Success Criteria

1. All existing tests pass
2. New tests for file size display pass
3. No breaking changes to API
4. Documentation updated
5. Works seamlessly in `4gpt` project
6. Size appears AFTER symlink target arrow: `"link -> target (1.2 KB)"` ✅
7. Uses `tree_print_lines.append()` not string concatenation ✅

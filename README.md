```markdown
# dir_tree

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Version](https://img.shields.io/badge/version-0.2.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)

`dir_tree` is a Python package that generates a directory tree structure in JSON format, with customizable options to exclude certain directories and files. It can be used as both a library in your Python projects and as a command-line tool.

## ✨ What's New in v0.2.0

- **File Size Display:** Optionally show human-readable file sizes (B, KB, MB, GB, TB) next to file names
- One-line integration for existing code: `show_file_sizes=True`
- CLI support: `dir-tree --show-file-sizes`
- See [CHANGELOG.md](CHANGELOG.md) for full details

## Features

- **Directory Tree Generation**: Generate a visual and JSON representation of a directory structure.
- **File Size Display**: Optionally display human-readable file sizes (B, KB, MB, GB, TB) next to file names.
- **Exclusion Options**: Exclude specific directories and files or file patterns.
- **Preferences Management**: Save and load preferences for exclusions.
- **Command-Line Interface**: Use the tool directly from the command line.

## Installation

### From Source

Clone the repository and install:

```bash
git clone https://github.com/krausality/dir_tree.git
cd dir_tree
pip install .
```

### From GitHub (Specific Version)

Install directly from a specific release:

```bash
# Latest version
pip install git+https://github.com/krausality/dir_tree.git

# Specific version
pip install git+https://github.com/krausality/dir_tree.git@v0.2.0
```


## 🛠  Development Mode (Editable Installs)

If you plan to **develop or modify this project locally**, it's recommended to use an **editable install**. This allows Python to load the package **directly from your source directory**, so any code changes are reflected immediately — no need to reinstall after every edit.

### Setup

```bash
cd dir_tree
python -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install --editable .
````

Once installed, you can run the tool in either of the following ways:

### ✅ Option 1: Module Invocation

```bash
python -m dir_tree COMMAND ...
```

  - Runs the package via the Python module system.
  - Always works inside an activated virtual environment.

### ✅ Option 2: Executable Invocation

```bash
dir_tree COMMAND ...
```

  - A **console script entry point** is automatically created during install.
  - On Windows: creates `dir_tree.exe` in `.venv\Scripts\`
  - On macOS/Linux: creates `dir_tree` in `.venv/bin/`

💡 **Pro tip**: Check where the executable lives with:

```bash
where dir_tree    # on Windows
which dir_tree    # on macOS/Linux
```

If the command isn’t found, make sure your virtual environment is activated and your PATH is correctly set.

-----

### Optional: Strict Editable Mode

If you want more control over which files are actually included in the package (e.g. to detect missing modules or simulate a release install), enable **strict mode**:

```bash
pip install -e . --config-settings editable_mode=strict
```

In this mode:

  - **New files won’t be exposed automatically** — you’ll need to reinstall to pick them up.
  - The install behaves more like a production wheel, which is useful for debugging packaging issues.

-----

### Notes

  - Code edits are reflected **immediately** in both normal and strict modes.
  - Any changes to **dependencies**, **entry-points**, or **project metadata** require reinstallation.
  - If you encounter import issues (especially with namespace packages), consider switching to a `src/`-based layout.  
      See the Python Packaging Authority’s recommendations for [modern package structures](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).

## Usage

### As a Python Library

You can use the `dir_tree` package in your Python scripts:

```python
from dir_tree import DirectoryTree, Preferences

# Initialize preferences
prefs = Preferences()
prefs.update_preferences(exclude_dirs=["env", "venv"], exclude_files=["*.log"])
prefs.save_preferences()  # Optionally save preferences for later use

# Generate directory tree
tree = DirectoryTree(
    root_dir="path/to/directory", 
    exclude_dirs=prefs.prefs["EXCLUDE_DIRS"], 
    exclude_files=prefs.prefs["EXCLUDE_FILES"]
)
print(tree.to_json())
```

#### With File Sizes

Display file sizes next to file names:

```python
from dir_tree import DirectoryTree

# Generate tree with file sizes
tree = DirectoryTree(
    root_dir=".",
    exclude_files={"*.pyc", "__pycache__"},
    show_file_sizes=True  # Enable file size display
)

import json
tree_data = json.loads(tree.to_json())
print(tree_data['tree_print'])
```

**Output:**
```
project/
├── README.md (8.6 KB)
├── setup.py (902.0 B)
└── src/
    ├── main.py (2.3 KB)
    └── utils.py (1.1 KB)
```

### Command-Line Interface (CLI)

After installing the package, you can use the `dir-tree` command in your terminal.

#### Basic Usage

Generate a directory tree starting from the current directory:

```bash
dir-tree
```

Specify a different directory:

```bash
dir-tree --dir /path/to/directory
```

#### Excluding Directories and Files

Exclude specific directories:

```bash
dir-tree --exclude-dir env venv node_modules
```

Exclude specific files or file patterns:

```bash
dir-tree --exclude-file "*.log" "*.tmp"
```

#### Display File Sizes

Show human-readable file sizes next to file names:

```bash
dir-tree --show-file-sizes
```

Or combine with other options:

```bash
dir-tree --dir /path/to/directory --exclude-file "*.pyc" --show-file-sizes
```

#### Saving and Loading Preferences

Save the current exclusions as preferences:

```bash
dir-tree --exclude-dir env venv --exclude-file "*.log" --save-prefs
```

Load previously saved preferences:

```bash
dir-tree --load-prefs
```

### JSON Output

The JSON output contains the following fields:

- **`root`**: The name of the root directory.
- **`tree`**: The directory structure as a nested dictionary.
- **`tree_print`**: A visual representation of the directory tree in text form (includes file sizes if enabled).
- **`excluded_dirs`**: A list of directories that were excluded.
- **`excluded_files`**: A list of files or file patterns that were excluded.

<details>
<summary>Click to see full JSON output example</summary>

```json
{
    "root": "example",
    "tree": {
        ".gptignore": null,
        "8_fileA.file": null,
        "8_fileA.jpg": null,
        "8_fileA.txt": null,
        "allfiles.txt": null,
        "exclude1": {
            "1_fileA.file": null,
            "1_fileA.jpg": null,
            "1_fileA.txt": null
        },
        "exclude2": {
            "2_fileC.file": null,
            "2_fileC.jpg": null,
            "2_fileC.txt": null,
            "sub_folder_ex2": {
                "5_fileC.txt": null
            }
        },
        "keep1": {
            "3_fileA.file": null,
            "3_fileA.jpg": null,
            "3_fileA.txt": null,
            "sub_folder_k1": {
                "4_fileB.file": null,
                "4_fileB.jpg": null,
                "4_fileB.txt": null
            }
        },
        "keep2": {
            "6_fileA.file": null,
            "6_fileA.jpg": null,
            "6_fileA.txt": null,
            "sub_folder_k2": {
                "7_fileA.file": null,
                "7_fileA.jpg": null,
                "7_fileA.txt": null
            }
        },
        "print_tree_dir.py": null
    },
    "tree_print": "example\n├── .gptignore\n├── 8_fileA.file\n├── 8_fileA.jpg\n├── 8_fileA.txt\n├── allfiles.txt\n├── exclude1\n│   ├── 1_fileA.file\n│   ├── 1_fileA.jpg\n│   └── 1_fileA.txt\n├── exclude2\n│   ├── 2_fileC.file\n│   ├── 2_fileC.jpg\n│   ├── 2_fileC.txt\n│   └── sub_folder_ex2\n│       └── 5_fileC.txt\n├── keep1\n│   ├── 3_fileA.file\n│   ├── 3_fileA.jpg\n│   ├── 3_fileA.txt\n│   └── sub_folder_k1\n│       ├── 4_fileB.file\n│       ├── 4_fileB.jpg\n│       └── 4_fileB.txt\n├── keep2\n│   ├── 6_fileA.file\n│   ├── 6_fileA.jpg\n│   ├── 6_fileA.txt\n│   └── sub_folder_k2\n│       ├── 7_fileA.file\n│       ├── 7_fileA.jpg\n│       └── 7_fileA.txt\n└── print_tree_dir.py",
    "excluded_dirs": [
        "env",
        "__pycache__",
        "node_modules",
        ".expo",
        ".idea",
        "venv",
        "dist",
        ".git",
        "build"
    ],
    "excluded_files": [
        "*.log",
        "LICENSE"
    ]
}
```

</details>

## Development

If you want to contribute or make changes to this package, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/dir_tree.git
    cd dir_tree
    ```

2. **Install the package in editable mode**:
    ```bash
    pip install -e .
    ```

3. **Run tests**:
    ```bash
    # Run the test suite
    python feature_development/file_size_display/test_file_sizes.py
    
    # Run demo to see file sizes in action
    python feature_development/file_size_display/demo_file_sizes.py
    ```

4. **Make your changes** and ensure tests pass

4. **Make your changes** and ensure tests pass

5. **Submit a pull request**:
    - Feel free to fork the repository and submit a pull request with your changes.

---

## 🔄 Release Process (For Maintainers)

### How to Create a New Release

When releasing a new version, follow these steps:

1. **Update the version in `setup.py`:**
   ```python
   setup(
       name='dir_tree',
       version='0.3.0',  # Increment version
       ...
   )
   ```

2. **Update `CHANGELOG.md`:**
   - Add a new section for the version
   - Document all changes

3. **Commit the changes:**
   ```bash
   git add setup.py CHANGELOG.md
   git commit -m "chore: Bump version to 0.3.0"
   ```

4. **Create and push a git tag:**
   ```bash
   # Create annotated tag
   git tag -a v0.3.0 -m "Release v0.3.0: Description of changes"
   
   # Push the tag to GitHub
   git push origin v0.3.0
   ```

5. **Verify the release:**
   ```bash
   git describe --tags  # Should show v0.3.0
   ```

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

**Example:**
- `0.1.0` → Initial release
- `0.2.0` → Added file size display feature (new feature, backward compatible)
- `0.2.1` → Would be a bug fix
- `1.0.0` → Would be the first stable release or a breaking change

---

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of all changes.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support & Contact

- **Issues & Bug Reports:** [GitHub Issues](https://github.com/krausality/dir_tree/issues)
- **Email:** krausality42@gmail.com
- **Repository:** [github.com/krausality/dir_tree](https://github.com/krausality/dir_tree)

---

Happy coding!
```

### Key Sections:

1. **Introduction**: Overview of the package.
2. **Features**: Highlight key features.
3. **Installation**: Instructions to install the package locally.
4. **Usage**: Demonstrates how to use the package as a library and via CLI.
5. **JSON Output**: Example of what the output looks like.
6. **Development**: Steps for contributing or making changes.
7. **License**: Information about the license.
8. **Contact**: How users can reach you for support or suggestions.

This `README.md` provides comprehensive documentation to help users understand, install, and use your package effectively.


---




-----

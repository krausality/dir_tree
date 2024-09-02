# dir_tree/directory_tree.py

import os
import fnmatch
import json
import argparse  # Import argparse for command-line functionality
from typing import List, Set, Dict, Optional, Any
from .preferences import Preferences  # Import Preferences from the package


class DirectoryTree:
    def __init__(self, root_dir: str, exclude_dirs: Optional[Set[str]] = None, exclude_files: Optional[Set[str]] = None):
        self.root_dir = root_dir
        self.exclude_dirs = exclude_dirs if exclude_dirs is not None else set()
        self.exclude_files = exclude_files if exclude_files is not None else set()
        self.tree = {}
        self.tree_print = ""

    def build_tree(self, current_dir: Optional[str] = None, prefix: str = '') -> Dict[str, Any]:
        if current_dir is None:
            current_dir = self.root_dir

        tree_structure = {}
        try:
            items = os.listdir(current_dir)
        except PermissionError:
            return {}

        filtered_items = [item for item in items
                          if item not in self.exclude_dirs and not self._file_should_be_excluded(item)]
        filtered_items.sort()

        for i, item in enumerate(filtered_items):
            item_path = os.path.join(current_dir, item)
            branch = '└── ' if i == len(filtered_items) - 1 else '├── '
            self.tree_print += f"{prefix}{branch}{item}\n"

            if os.path.isdir(item_path):
                tree_structure[item] = self.build_tree(item_path, prefix + ('    ' if i == len(filtered_items) - 1 else '│   '))
            else:
                tree_structure[item] = None

        return tree_structure

    def _file_should_be_excluded(self, file_name: str) -> bool:
        return any(fnmatch.fnmatch(file_name, pattern) for pattern in self.exclude_files)

    def to_json(self) -> str:
        self.tree = self.build_tree()
        root_display = f"{os.path.basename(self.root_dir)}\n"  # Add the root directory to the beginning of the tree print
        tree_output = root_display + self.tree_print.rstrip()  # Add the tree structure, without trailing newline
        return json.dumps({
            "root": os.path.basename(self.root_dir),
            "tree": self.tree,
            "tree_print": tree_output,  # Include the properly formatted tree string
            "excluded_dirs": list(self.exclude_dirs),
            "excluded_files": list(self.exclude_files)
        }, indent=4, ensure_ascii=False)  # ensure_ascii=False to avoid Unicode escaping


def main():
    # Command-line interface
    parser = argparse.ArgumentParser(description='Generate a directory tree structure as JSON.')
    parser.add_argument('--dir', type=str, default=os.getcwd(),
                        help='The directory to start from (default is current directory).')
    parser.add_argument('--exclude-dir', type=str, nargs='*',
                        help='Directories to exclude from the tree.')
    parser.add_argument('--exclude-file', type=str, nargs='*',
                        help='Files or patterns to exclude from the tree.')
    parser.add_argument('--save-prefs', action='store_true',
                        help='Save the current preferences for future use.')
    parser.add_argument('--load-prefs', action='store_true',
                        help='Load saved preferences before generating the tree.')

    args = parser.parse_args()

    prefs = Preferences()

    if args.load_prefs:
        prefs = Preferences()

    if args.exclude_dir:
        prefs.update_preferences(exclude_dirs=args.exclude_dir)
    if args.exclude_file:
        prefs.update_preferences(exclude_files=args.exclude_file)

    if args.save_prefs:
        prefs.save_preferences()

    tree = DirectoryTree(root_dir=args.dir, exclude_dirs=prefs.prefs["EXCLUDE_DIRS"], exclude_files=prefs.prefs["EXCLUDE_FILES"])

    # Convert the JSON string back to a Python dictionary
    tree_dict = json.loads(tree.to_json())

    # Access and print the "tree_print" part of the output
    print(tree_dict['tree_print'])


if __name__ == "__main__":
    main()

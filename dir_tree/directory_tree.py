import os
import fnmatch
import json
import argparse
from typing import List, Set, Dict, Optional, Any
# Assuming preferences.py is in the same package directory
from .preferences import Preferences


class DirectoryTree:
    def __init__(self, root_dir: str,
                 exclude_dirs: Optional[Set[str]] = None,
                 exclude_files: Optional[Set[str]] = None,
                 follow_symlinks_in_tree: bool = False): # NEU: follow_symlinks_in_tree
        self.root_dir = os.path.abspath(root_dir) # Use absolute path for consistency
        self.exclude_dirs = exclude_dirs if exclude_dirs is not None else set()
        self.exclude_files = exclude_files if exclude_files is not None else set()
        self.follow_symlinks_in_tree = follow_symlinks_in_tree # NEU: Speichern
        self.tree = {}
        self.tree_print_lines = [] # Store lines for easier construction

    def _should_be_excluded(self, item_name: str, item_path: str) -> bool:
        if item_name in self.exclude_dirs: # Direct directory name exclusion
            return True
        if os.path.isdir(item_path) and any(fnmatch.fnmatch(item_name, pattern) for pattern in self.exclude_dirs): # Pattern for dir names
             return True
        if not os.path.isdir(item_path) and any(fnmatch.fnmatch(item_name, pattern) for pattern in self.exclude_files): # Pattern for file names
            return True
        return False

    def build_tree_recursive(self, current_dir: str, prefix: str = '') -> Dict[str, Any]:
        tree_structure = {}
        try:
            # os.listdir() does not follow symlinks for the current_dir itself,
            # it lists entries within the directory current_dir points to.
            # If current_dir is a symlink to a directory, os.listdir lists contents of the target.
            items = os.listdir(current_dir)
        except PermissionError:
            self.tree_print_lines.append(f"{prefix}└── [Permission Denied]")
            return {"[Permission Denied]": None}
        except FileNotFoundError:
            self.tree_print_lines.append(f"{prefix}└── [Not Found or Broken Symlink]")
            return {"[Not Found or Broken Symlink]": None}


        # Filter items based on exclusion rules BEFORE sorting
        # This avoids issues where sorting changes order then filtering removes an item
        # that affects the '└──' vs '├──' logic for the *next* visible item.
        
        # We need to check each item individually before adding to a list to sort
        processable_items = []
        for item_name in items:
            item_path = os.path.join(current_dir, item_name)
            if not self._should_be_excluded(item_name, item_path):
                processable_items.append(item_name)
        
        processable_items.sort() # Sort the filtered list

        for i, item_name in enumerate(processable_items):
            item_path = os.path.join(current_dir, item_name)
            is_last_item = (i == len(processable_items) - 1)
            connector = '└── ' if is_last_item else '├── '
            
            entry_display_name = item_name
            is_symlink = os.path.islink(item_path)

            if is_symlink:
                try:
                    target_path = os.readlink(item_path)
                    # Try to make target_path relative if it's within the root_dir scope, else absolute
                    try:
                        relative_target = os.path.relpath(os.path.realpath(item_path), os.path.dirname(item_path))
                        entry_display_name += f" -> {relative_target}"
                    except ValueError: # If paths are on different drives (Windows)
                        entry_display_name += f" -> {target_path}" # Fallback to raw target
                except OSError: # Broken symlink
                    entry_display_name += " -> [Broken Symlink]"
                    target_path = "[Broken Symlink]"


            # Check if it's a directory (or a symlink pointing to a directory)
            # os.path.isdir() follows symlinks by default.
            is_target_dir = os.path.isdir(item_path)

            if is_target_dir:
                # If it's a symlink to a directory AND we are NOT following symlinks in tree
                if is_symlink and not self.follow_symlinks_in_tree:
                    self.tree_print_lines.append(f"{prefix}{connector}{entry_display_name}")
                    tree_structure[item_name] = {"symlink_target": target_path} # Mark as non-expanded symlink
                else: # Regular directory or symlink to dir that we DO follow
                    self.tree_print_lines.append(f"{prefix}{connector}{entry_display_name}")
                    new_prefix = prefix + ('    ' if is_last_item else '│   ')
                    # If current_dir itself was a symlink, item_path is relative to its target.
                    # For recursion, os.path.isdir(item_path) already confirmed it's a dir (or symlink to it).
                    # os.listdir(item_path) will correctly list contents of the target if item_path is a symlink to a dir.
                    tree_structure[item_name] = self.build_tree_recursive(item_path, new_prefix)
            else: # File or symlink to file (or broken symlink treated as non-directory)
                self.tree_print_lines.append(f"{prefix}{connector}{entry_display_name}")
                tree_structure[item_name] = None # Represents a file

        return tree_structure

    def to_json(self) -> str:
        self.tree_print_lines = [] # Reset for multiple calls if any
        # Start building the tree structure and the print representation
        self.tree = self.build_tree_recursive(self.root_dir)
        
        # The root directory name itself should be the first line of tree_print
        root_display_name = os.path.basename(self.root_dir)
        if os.path.islink(self.root_dir): # If root_dir itself is a symlink
            try:
                target = os.readlink(self.root_dir)
                root_display_name += f" -> {target}"
            except OSError:
                 root_display_name += f" -> [Broken Symlink]"

        final_tree_print = root_display_name + "\n" + "\n".join(self.tree_print_lines)
        
        return json.dumps({
            "root": os.path.basename(self.root_dir), # Keep original root name
            "tree": self.tree,
            "tree_print": final_tree_print.rstrip(),
            "excluded_dirs": list(self.exclude_dirs), # Convert set to list for JSON
            "excluded_files": list(self.exclude_files) # Convert set to list for JSON
        }, indent=4, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Generate a directory tree structure as JSON.')
    parser.add_argument('--dir', type=str, default=os.getcwd(),
                        help='The directory to start from (default is current directory).')
    parser.add_argument('--exclude-dir', type=str, nargs='*', default=[],
                        help='Directories to exclude (names or fnmatch patterns).')
    parser.add_argument('--exclude-file', type=str, nargs='*', default=[],
                        help='Files to exclude (names or fnmatch patterns).')
    parser.add_argument('--save-prefs', action='store_true',
                        help='Save the current exclusion preferences.')
    parser.add_argument('--load-prefs', action='store_true',
                        help='Load saved exclusion preferences.')
    # NEU: --follow-symlinks-in-tree for dir-tree CLI
    parser.add_argument('--follow-symlinks-in-tree', action='store_true',
                        help='Follow symbolic links to directories when generating the tree structure view.')


    args = parser.parse_args()
    prefs = Preferences() # Uses default prefs initially

    if args.load_prefs:
        prefs.load_preferences() # Reloads from file, potentially overriding defaults

    # Apply CLI exclusions (these will be added to whatever prefs loaded)
    if args.exclude_dir:
        prefs.update_preferences(exclude_dirs=args.exclude_dir)
    if args.exclude_file:
        prefs.update_preferences(exclude_files=args.exclude_file)

    if args.save_prefs:
        prefs.save_preferences()

    # Use the follow_symlinks_in_tree flag from CLI args for DirectoryTree
    tree_generator = DirectoryTree(
        root_dir=args.dir,
        exclude_dirs=prefs.prefs["EXCLUDE_DIRS"],
        exclude_files=prefs.prefs["EXCLUDE_FILES"],
        follow_symlinks_in_tree=args.follow_symlinks_in_tree # Pass the CLI flag
    )

    tree_json_str = tree_generator.to_json()
    tree_data = json.loads(tree_json_str)
    print(tree_data['tree_print'])


if __name__ == "__main__":
    main()
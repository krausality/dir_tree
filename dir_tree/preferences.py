# dir_tree/preferences.py

import os
import json
from typing import Dict, Set, List, Optional

DEFAULT_PREFS: Dict[str, Set[str]] = {
    "EXCLUDE_DIRS": {'venv', 'env', 'node_modules', 'dist', '.idea', '.expo', '.git', '__pycache__'},
    "EXCLUDE_FILES": {"LICENSE", "dir_tree_prefs.json"}
}

PREFS_FILE: str = "./dir_tree_prefs.json"


class Preferences:
    def __init__(self, prefs_file: str = PREFS_FILE):
        self.prefs_file = prefs_file
        self.prefs = self.load_preferences()

    def load_preferences(self) -> Dict[str, Set[str]]:
        try:
            if os.path.exists(self.prefs_file):
                with open(self.prefs_file, "r") as file:
                    loaded_prefs = json.load(file)
                    return {key: set(value) for key, value in loaded_prefs.items()}
        except json.JSONDecodeError as e:
            print(f"Error loading preferences: {e}. Using default preferences.")
        return DEFAULT_PREFS

    def save_preferences(self) -> None:
        try:
            serializable_prefs = {key: list(value) for key, value in self.prefs.items()}
            with open(self.prefs_file, "w") as file:
                json.dump(serializable_prefs, file, indent=4)
        except IOError as e:
            print(f"Error saving preferences: {e}. Changes might not be saved.")

    def update_preferences(self, exclude_dirs: Optional[List[str]] = None, exclude_files: Optional[List[str]] = None) -> None:
        if exclude_dirs:
            self.prefs["EXCLUDE_DIRS"].update(exclude_dirs)
        if exclude_files:
            self.prefs["EXCLUDE_FILES"].update(exclude_files)

    def include_back(self, include_dirs: Optional[List[str]] = None, include_files: Optional[List[str]] = None) -> None:
        if include_dirs:
            self.prefs["EXCLUDE_DIRS"].difference_update(include_dirs)
        if include_files:
            self.prefs["EXCLUDE_FILES"].difference_update(include_files)

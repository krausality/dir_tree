import os
import fnmatch
import json
import argparse
from typing import List, Set, Dict, Optional, Any
from .preferences import Preferences # Stellt sicher, dass preferences.py im selben Paket ist


class DirectoryTree:
    def __init__(self, root_dir: str,
                 exclude_dirs: Optional[Set[str]] = None,
                 exclude_files: Optional[Set[str]] = None,
                 follow_symlinks_in_tree: bool = False):
        self.root_dir = os.path.abspath(root_dir)
        # `exclude_dirs` von 4gpt ist jetzt immer ein leeres Set.
        # Alle Muster (für Dateien und Verzeichnisse) kommen über `exclude_files`.
        self.explicit_exclude_dir_names = exclude_dirs if exclude_dirs is not None else set()
        self.general_exclude_patterns = exclude_files if exclude_files is not None else set()
        self.follow_symlinks_in_tree = follow_symlinks_in_tree
        self.tree = {}
        self.tree_print_lines = [] # Zum Sammeln der Ausgabezeilen für tree_print

        # DEBUG: Zeige, welche Exclude-Patterns bei der Initialisierung ankommen
        # print(f"[DIR_TREE INIT] root_dir: {self.root_dir}")
        # print(f"[DIR_TREE INIT] explicit_exclude_dir_names: {self.explicit_exclude_dir_names}")
        # print(f"[DIR_TREE INIT] general_exclude_patterns: {self.general_exclude_patterns}")
        # print(f"[DIR_TREE INIT] follow_symlinks_in_tree: {self.follow_symlinks_in_tree}")

    def _should_be_excluded(self, item_name: str, item_path: str) -> bool:
        # print(f"[DIR_TREE EXCLUDE CHECK] Item: '{item_name}', Path: '{item_path}'")

        # 1. Explizite Verzeichnisnamen-Ausschlüsse (wird von 4gpt nicht genutzt, da exclude_dirs=set() übergeben wird)
        if os.path.isdir(item_path) and item_name in self.explicit_exclude_dir_names:
            # print(f"  -> EXCLUDED (explicit dir name): {item_name}")
            return True

        # 2. Allgemeine Muster-Ausschlüsse (fnmatch auf item_name)
        #    Diese Muster gelten für Datei- UND Verzeichnisnamen.
        for pattern in self.general_exclude_patterns:
            if fnmatch.fnmatch(item_name, pattern):
                # print(f"  -> EXCLUDED (general pattern '{pattern}' matched '{item_name}')")
                return True
        
        # print(f"  -> NOT EXCLUDED: {item_name}")
        return False

    def build_tree_recursive(self, current_dir: str, prefix: str = '') -> Dict[str, Any]:
        tree_structure = {}
        try:
            items_in_dir = os.listdir(current_dir)
        except PermissionError:
            self.tree_print_lines.append(f"{prefix}└── [Permission Denied]")
            return {"[Permission Denied]": None}
        except FileNotFoundError: # z.B. wenn current_dir ein broken symlink war
            self.tree_print_lines.append(f"{prefix}└── [Directory Not Found or Broken Symlink Target]")
            return {"[Directory Not Found or Broken Symlink Target]": None}

        processable_items = []
        for item_name in items_in_dir:
            item_path = os.path.join(current_dir, item_name)
            if not self._should_be_excluded(item_name, item_path):
                processable_items.append(item_name)
        
        processable_items.sort()

        for i, item_name in enumerate(processable_items):
            item_path = os.path.join(current_dir, item_name)
            is_last_item = (i == len(processable_items) - 1)
            connector = '└── ' if is_last_item else '├── '
            
            entry_display_name = item_name
            is_symlink = os.path.islink(item_path)
            symlink_target_info = "" # Für die JSON-Struktur, falls es ein nicht gefolgter Symlink ist

            if is_symlink:
                try:
                    target_path = os.readlink(item_path)
                    # Versuche, den Zielpfad relativ zum Symlink-Verzeichnis darzustellen
                    try:
                        # realpath löst alle Symlinks im Pfad auf, um den kanonischen Pfad zu erhalten
                        resolved_target_path = os.path.realpath(item_path)
                        # relpath vom Verzeichnis des Symlinks zum aufgelösten Ziel
                        relative_target = os.path.relpath(resolved_target_path, os.path.dirname(item_path))
                        entry_display_name += f" -> {relative_target}"
                        symlink_target_info = relative_target
                    except ValueError: # z.B. Pfade auf unterschiedlichen Laufwerken (Windows)
                        entry_display_name += f" -> {target_path}"
                        symlink_target_info = str(target_path)
                except OSError: # Fehler beim Lesen des Symlink-Ziels (z.B. broken symlink)
                    entry_display_name += " -> [Broken Symlink]"
                    symlink_target_info = "[Broken Symlink]"

            is_target_a_directory = os.path.isdir(item_path) # os.path.isdir folgt Symlinks!

            if is_target_a_directory:
                # Wenn es ein Symlink zu einem Verzeichnis ist UND wir Symlinks NICHT folgen sollen
                if is_symlink and not self.follow_symlinks_in_tree:
                    self.tree_print_lines.append(f"{prefix}{connector}{entry_display_name}")
                    tree_structure[item_name] = {"symlink_target": symlink_target_info, "_type": "dir_symlink_no_follow"}
                else: # Reguläres Verzeichnis oder Symlink zu Verzeichnis, dem wir folgen
                    # Wenn wir folgen, zeigen wir nur den Linknamen (oder originalen Namen) im Baum
                    self.tree_print_lines.append(f"{prefix}{connector}{item_name if not is_symlink else entry_display_name.split(' -> ')[0]}")
                    new_prefix = prefix + ('    ' if is_last_item else '│   ')
                    tree_structure[item_name] = self.build_tree_recursive(item_path, new_prefix)
            else: # Datei, Symlink zu Datei oder etwas, das kein Verzeichnis ist
                self.tree_print_lines.append(f"{prefix}{connector}{entry_display_name}")
                tree_structure[item_name] = None # Repräsentiert eine Datei oder ein Blatt im Baum

        return tree_structure

    def to_json(self) -> str:
        self.tree_print_lines = [] # Zurücksetzen für den Fall mehrmaliger Aufrufe
        self.tree = self.build_tree_recursive(self.root_dir)
        
        root_display_name = os.path.basename(self.root_dir)
        if os.path.islink(self.root_dir):
            try:
                target = os.readlink(self.root_dir)
                root_display_name += f" -> {target}"
            except OSError:
                 root_display_name += " -> [Broken Symlink]"

        final_tree_print = root_display_name + "\n" + "\n".join(self.tree_print_lines)
        
        return json.dumps({
            "root": os.path.basename(self.root_dir),
            "tree": self.tree,
            "tree_print": final_tree_print.rstrip(),
            "excluded_dirs": list(self.explicit_exclude_dir_names), # Sollte leer sein von 4gpt
            "excluded_files": list(self.general_exclude_patterns) # Enthält alle Muster
        }, indent=4, ensure_ascii=False)


def main(): # CLI für dir-tree standalone
    parser = argparse.ArgumentParser(description='Generate a directory tree structure as JSON.')
    parser.add_argument('--dir', type=str, default=os.getcwd(),
                        help='The directory to start from (default is current directory).')
    parser.add_argument('--exclude-dir', type=str, nargs='*', default=[],
                        help='Directories to exclude by exact name.')
    parser.add_argument('--exclude-file', type=str, nargs='*', default=[],
                        help='Files or directories to exclude by fnmatch pattern.')
    parser.add_argument('--save-prefs', action='store_true',
                        help='Save the current exclusion preferences.')
    parser.add_argument('--load-prefs', action='store_true',
                        help='Load saved exclusion preferences.')
    parser.add_argument('--follow-symlinks-in-tree', action='store_true',
                        help='Follow symbolic links to directories when generating the tree structure view.')

    args = parser.parse_args()
    prefs = Preferences()

    if args.load_prefs:
        prefs.load_preferences() # Lädt aus Datei, überschreibt Standardeinstellungen

    # CLI-Argumente aktualisieren die geladenen/Standard-Präferenzen
    if args.exclude_dir: # Explizite Verzeichnisnamen
        prefs.update_preferences(exclude_dirs=args.exclude_dir)
    if args.exclude_file: # Muster für Dateien/Verzeichnisse
        prefs.update_preferences(exclude_files=args.exclude_file) # Geht in EXCLUDE_FILES der Prefs

    if args.save_prefs:
        prefs.save_preferences()

    # Für die dir-tree CLI:
    # exclude_dirs kommt aus prefs["EXCLUDE_DIRS"]
    # exclude_files kommt aus prefs["EXCLUDE_FILES"]
    tree_generator = DirectoryTree(
        root_dir=args.dir,
        exclude_dirs=prefs.prefs.get("EXCLUDE_DIRS", set()), # Explizite Verzeichnisnamen
        exclude_files=prefs.prefs.get("EXCLUDE_FILES", set()), # Muster für Dateien und Verzeichnisse
        follow_symlinks_in_tree=args.follow_symlinks_in_tree
    )

    tree_json_str = tree_generator.to_json()
    tree_data = json.loads(tree_json_str)
    print(tree_data['tree_print'])


if __name__ == "__main__":
    main()
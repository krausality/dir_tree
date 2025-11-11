# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-12

### Added
- **File Size Display Feature**: Optional display of human-readable file sizes next to file names
  - New parameter `show_file_sizes` in `DirectoryTree` constructor (default: `False`)
  - Automatic size formatting in B, KB, MB, GB, TB units
  - Always displays 1 decimal place (e.g., "1.5 KB", "100.0 B")
  - Only files show sizes; directories never display sizes
  - Symlinks show target file size (not symlink size)
  - Graceful error handling for permission errors and broken symlinks
  - Fully backward compatible (opt-in feature)

### Technical Details
- Added `_format_size()` method for converting bytes to human-readable format
- Modified file handling in `build_tree_recursive()` to conditionally append sizes
- Size information appears in `tree_print` output field
- No changes to nested `tree` JSON structure (maintains compatibility)
- Performance impact: ~20% overhead when enabled (acceptable for opt-in feature)

### Documentation
- Updated README.md with file size display examples
- Added comprehensive test suite in `feature_development/` directory
- Created detailed implementation documentation

## [0.1.0] - Initial Release

### Added
- Directory tree generation with JSON output
- Customizable exclusion patterns for files and directories
- Symlink support with optional following
- Preference management system
- Command-line interface
- Visual tree representation in `tree_print` field

### Features
- Recursive directory traversal
- Pattern-based exclusions using fnmatch
- Graceful error handling for permission errors
- Support for broken symlinks
- Cross-platform compatibility (Windows, macOS, Linux)

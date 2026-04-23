# Akasha Data Directory

This directory contains all Akasha persistent data.

## Structure

- `projects/` - Project definitions and metadata
- `tasks/` - Task management data
- `knowledge/` - Three-level knowledge hierarchy
  - `facts/` - Level 1: Immutable truths
  - `patterns/` - Level 2: Proven approaches
  - `insights/` - Level 3: Contextual learnings
- `versions/` - Frozen versions and branches
- `plans/` - Plan evolution and discussions
- `sessions/` - Session context persistence
- `topics/` - Research topics
- `meta/` - System metadata

## Important

This directory is mounted from your Windows filesystem.
If you encounter permission issues, run `fix-permissions.bat` as Administrator.

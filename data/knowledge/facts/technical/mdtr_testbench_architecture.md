---
category: technical
created: '2025-08-28T08:52:29.665412'
hash: c3e8a9ac3fe7a128
immutable: true
level: 1
level_name: facts
metadata:
  tags:
  - mdtr
  - testbench
  - architecture
  - plugins
modified: '2025-08-28T08:52:29.665420'
sources:
- MDTR Testbench Implementation
- Plugin Architecture Documentation
title: MDTR Testbench Architecture
---

The MDTR Text Encoding Testbench is a production-ready plugin-based framework for systematically experimenting with text encoding approaches using Multi-Dimensional Topology Resonators.

**Core Architecture:**
- **PluginManager**: Discovers and loads term/rule encoder plugins from plugins/ directory
- **ExperimentManager**: Manages experiment lifecycle, chains, and archival
- **ExperimentChain**: Multi-phase experiments with dependency management
- **TermEncoderPlugin**: Abstract base for vocabulary encoding strategies
- **RuleEncoderPlugin**: Abstract base for grammar/style rule encoding

**Directory Structure:**
```
/projects/atlas/klein_fnn/mdtr_txt_bench/
├── core.py                  # Core framework classes
├── cli.py                   # Command-line interface
├── plugins/                 # Plugin directory
│   ├── term_encoders/       # Term encoding plugins
│   └── rule_encoders/       # Rule encoding plugins
├── templates/               # Experiment templates
├── experiments/             # Active experiments
├── archive/                 # Archived experiments
├── chains/                  # Chain definitions
└── configs/                 # Configuration files
```

**Key Concepts:**
- **Terms**: Vocabulary elements (words, concepts) - base frequency patterns
- **Rules**: Grammar/style modifications - phase/amplitude modulations
- **Phases**: Individual experiment steps with success criteria
- **Chains**: Sequences of phases with dependencies
- **Templates**: Reusable experiment configurations

**Location**: `/projects/atlas/klein_fnn/mdtr_txt_bench/`
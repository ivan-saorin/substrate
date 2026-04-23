---
category: technical
created: '2025-08-28T08:55:06.129076'
hash: b618a8df831efea3
immutable: true
level: 1
level_name: facts
metadata:
  tags:
  - mdtr
  - testbench
  - cli
  - commands
  - reference
modified: '2025-08-28T08:55:06.129085'
sources:
- MDTR Testbench CLI
- Command Documentation
title: MDTR Testbench CLI Reference
---

**MDTR Testbench CLI Command Reference:**

**Location**: `/projects/atlas/klein_fnn/mdtr_txt_bench/`

**Core Commands:**

```bash
# Plugin Management
python cli.py plugins                    # List all available plugins
python cli.py templates                  # List available experiment templates

# Experiment Creation
python cli.py create template_name --name experiment_name
python cli.py create basic_encoding_test --name my_test
python cli.py create template --name test --param dim 256 --param vocab_size 100

# Experiment Execution  
python cli.py run chain_id               # Run complete experiment chain
python cli.py run chain_id --phase specific_phase  # Run single phase

# Status and Results
python cli.py list                       # List all experiment chains
python cli.py list --status completed   # Filter by status
python cli.py status chain_id           # Show detailed chain status
python cli.py results chain_id          # View experiment results
python cli.py results chain_id --phase phase_name --format json

# Management
python cli.py archive chain_id --reason "description"  # Archive experiment
python cli.py cleanup --days 7          # Archive failed experiments >7 days old
python cli.py cleanup --days 7 --dry-run  # Preview cleanup actions
```

**Chain ID Format**: `experiment_name_YYYYMMDD_HHMMSS`

**Status Values**: `created`, `running`, `completed`, `failed`, `archived`

**File Locations**:
- Active experiments: `experiments/`
- Archived experiments: `archive/YYYYMMDD/`
- Chain definitions: `chains/`
- Templates: `templates/`
- System logs: `testbench.log`

**Quick Validation**:
```bash
python test_setup.py                    # Verify setup works
cd /projects/atlas/klein_fnn/mdtr_txt_bench && python cli.py plugins
```

**Parameter Passing**:
- JSON file: `--params config.json`
- Individual values: `--param key value`
- Multiple params: `--param dim 512 --param vocab_size 1000`

**Common Flags**:
- `--verbose` or `-v`: Enable verbose output
- `--dry-run`: Preview actions without executing
- `--format json`: Output results as JSON
- `--details`: Show detailed information
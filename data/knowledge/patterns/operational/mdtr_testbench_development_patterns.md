---
category: operational
created: '2025-08-28T08:52:54.743945'
hash: 446afdfc28a5f5c2
immutable: false
level: 2
level_name: patterns
metadata:
  tags:
  - mdtr
  - testbench
  - patterns
  - development
modified: '2025-08-28T08:52:54.743954'
sources:
- MDTR Testbench Usage
- Plugin Development Guide
title: MDTR Testbench Development Patterns
---

**Plugin Development Pattern for MDTR Testbench:**

**Term Encoder Plugin Structure:**
1. Inherit from `TermEncoderPlugin`
2. Implement required methods:
   - `encode_term(term: str) -> np.ndarray`
   - `decode_pattern(pattern: np.ndarray) -> str` 
   - `get_vocabulary() -> List[str]`
3. Define plugin metadata properties
4. Create factory function `create_plugin(**kwargs)`

**Rule Encoder Plugin Structure:**
1. Inherit from `RuleEncoderPlugin`
2. Implement required methods:
   - `encode_rule(rule_type: str, context: Dict) -> np.ndarray`
   - `apply_rule(term_pattern, rule_pattern) -> np.ndarray`
   - `get_rules() -> List[str]`
3. Define transformation types (phase_shift, amplitude_scale, etc.)

**Experiment Creation Pattern:**
1. Create template JSON with phases array
2. Each phase specifies: term_encoder, rule_encoder, mdtr_config, test_data, success_criteria
3. Use dependency chains: `depends_on: ["previous_phase"]`
4. Set reasonable success criteria and timeouts

**File Naming Conventions:**
- Plugin files: `category_approach.py` (e.g., `frequency_basic.py`)
- Templates: `purpose_description.json` (e.g., `basic_encoding_test.json`)
- Experiments: auto-generated with timestamps

**CLI Usage Pattern:**
```bash
python cli.py create template_name --name experiment_name
python cli.py run experiment_chain_id
python cli.py archive experiment_chain_id --reason "description"
```
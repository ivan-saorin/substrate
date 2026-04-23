---
category: architectural
created: '2025-08-28T08:53:48.612484'
hash: f31d6bf0efcda220
immutable: false
level: 2
level_name: patterns
metadata:
  tags:
  - mdtr
  - testbench
  - plugin-development
  - step-by-step
modified: '2025-08-28T08:53:48.612499'
sources:
- Plugin Development Experience
- MDTR Testbench Implementation
title: MDTR Testbench Plugin Development Guide
---

**Step-by-Step Plugin Development for MDTR Testbench:**

**Creating a Term Encoder Plugin:**

1. **Create Plugin File**: `plugins/term_encoders/my_encoder.py`

2. **Basic Structure Template**:
```python
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from core import TermEncoderPlugin

class MyTermEncoder(TermEncoderPlugin):
    @property
    def plugin_name(self) -> str:
        return "my_encoder"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        return "Description of encoding approach"
    
    def encode_term(self, term: str) -> np.ndarray:
        # Return complex frequency pattern
        pass
    
    def decode_pattern(self, pattern: np.ndarray) -> str:
        # Return most likely term
        pass
    
    def get_vocabulary(self) -> List[str]:
        # Return available terms
        pass

def create_plugin(**kwargs):
    return MyTermEncoder(**kwargs)
```

3. **Test Plugin**: Run `python test_setup.py` to verify loading

**Creating a Rule Encoder Plugin:**

1. **Create Plugin File**: `plugins/rule_encoders/my_rules.py`

2. **Define Rule Transformations**:
   - `phase_shift`: `pattern *= np.exp(1j * amount)`
   - `amplitude_scale`: `pattern *= amount`
   - `frequency_shift`: Circular shift pattern indices
   - `harmonic_modulation`: Boost/suppress harmonic frequencies

3. **Implement Core Methods**:
   - `encode_rule()`: Create modulation pattern
   - `apply_rule()`: Apply pattern * modulation
   - `get_rules()`: Return available rule names

**Experiment Template Creation:**

1. **Create Template**: `templates/my_experiment.json`
2. **Define Phase Structure**:
   - Each phase tests specific capability
   - Set dependencies between phases
   - Define realistic success criteria
3. **Test Data Selection**:
   - Use domain-relevant text samples
   - Include edge cases and variations
   - Keep samples short for quick iteration

**Plugin Integration Testing**:
1. Roundtrip accuracy test for term encoders
2. Rule effect measurement for rule encoders  
3. MDTR integration validation
4. Performance benchmarking
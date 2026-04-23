---
category: lessons_learned
created: '2025-08-28T08:53:31.899714'
hash: 65f41ee8ae999ed4
immutable: false
level: 3
level_name: insights
metadata:
  tags:
  - mdtr
  - testbench
  - best-practices
  - golden-rules
modified: '2025-08-28T08:53:31.899721'
sources:
- MDTR Testbench Experience
- Production Usage Insights
title: MDTR Testbench Golden Rules and Best Practices
---

**MDTR Testbench Golden Rules and Best Practices:**

**🟢 DO's - Golden Rules:**

1. **Start Simple**: Begin with `basic_encoding_test` template before creating custom experiments
2. **Plugin Factory Pattern**: Always include `create_plugin(**kwargs)` factory function in plugins
3. **Validate Early**: Run `test_setup.py` after any plugin changes to catch issues immediately
4. **Dependency Management**: Use phase dependencies (`depends_on`) to ensure proper experiment sequencing
5. **Archive Regularly**: Archive completed experiments to prevent directory bloat
6. **Document Success Criteria**: Set realistic, measurable success thresholds for each phase
7. **Version Control**: Tag plugin versions and track what works for reproducibility

**🔴 DON'Ts - Common Pitfalls:**

1. **Don't Skip Validation**: Never skip roundtrip testing for term encoders - encoding/decoding fidelity is critical
2. **Don't Hardcode Dimensions**: Always make frequency dimensions configurable in plugins
3. **Don't Ignore Dependencies**: Skipping phase dependencies leads to meaningless results
4. **Don't Proliferate Files**: Don't create one-off experiment scripts - use the template system
5. **Don't Set Impossible Criteria**: Avoid success criteria >0.9 unless you've validated it's achievable
6. **Don't Mix Concerns**: Keep term encoding separate from rule application logic
7. **Don't Forget Error Handling**: Plugin crashes break entire experiment chains

**⚡ Quick Wins:**

- Use `--dry-run` flags for cleanup operations
- Set `timeout_minutes` appropriately (10-30 for most phases)
- Tag experiments with meaningful descriptors
- Use `verbose` mode for debugging plugin issues
- Keep plugin vocabularies small initially (50-100 terms)

**🔧 Troubleshooting Patterns:**

- Plugin won't load → Check import paths and factory function
- Experiment fails → Review success criteria and test data
- Results inconsistent → Validate encoder roundtrip accuracy first
- Memory issues → Reduce frequency dimensions or batch size
- Chain hangs → Set appropriate timeouts on long-running phases

**📊 Success Metrics Guidelines:**
- Term roundtrip accuracy: 0.7-0.9 (realistic range)
- MDTR learning rate: 0.4-0.7 (depends on pattern complexity) 
- Rule consistency: >0.5 (ensure rules have measurable effects)

**🎯 Creative Writing Focus:**
- Test emotional frequency mapping with literary vocabulary
- Use longer test sequences for narrative coherence validation
- Include style transfer experiments with author-specific patterns
- Validate long-range dependency preservation in generated text
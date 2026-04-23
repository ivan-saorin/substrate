---
category: experimental
created: '2025-08-28T08:54:48.602969'
hash: ea0cc76f15bef497
immutable: false
level: 3
level_name: insights
metadata:
  tags:
  - mdtr
  - testbench
  - troubleshooting
  - debugging
modified: '2025-08-28T08:54:48.602977'
sources:
- MDTR Testbench Debugging
- Production Issues
title: MDTR Testbench Troubleshooting Guide
---

**MDTR Testbench Troubleshooting and Common Issues:**

**Plugin Loading Issues:**

*Problem*: Plugin not found or fails to load
*Solutions*:
- Verify plugin file is in correct directory (`plugins/term_encoders/` or `plugins/rule_encoders/`)
- Check `create_plugin(**kwargs)` factory function exists
- Ensure all imports are correct (especially parent directory import)
- Run `python test_setup.py` to debug loading issues
- Check plugin inherits from correct base class (`TermEncoderPlugin` or `RuleEncoderPlugin`)

**Experiment Execution Problems:**

*Problem*: Experiment fails with phase errors
*Solutions*:
- Review success criteria - may be too strict (>0.9 often unrealistic)
- Check test data quality - avoid empty strings or very long sequences
- Verify plugin configuration parameters match what plugin expects
- Increase timeout_minutes for complex phases
- Check dependencies are met (`depends_on` phases completed successfully)

**MDTR Integration Issues:**

*Problem*: MDTR learning fails or returns zero patterns
*Solutions*:
- Verify your MDTR code is in Python path
- Check frequency patterns are complex arrays, not real
- Ensure pattern dimensions match MDTR expectations (typically 512)
- Test with smaller vocabularies first (10-50 terms)
- Validate encoder roundtrip accuracy >0.7 before MDTR testing

**Memory and Performance:**

*Problem*: Out of memory or very slow execution
*Solutions*:
- Reduce frequency dimensions (256 instead of 512)
- Limit vocabulary size in plugins
- Use smaller test datasets
- Set appropriate timeouts
- Run experiments sequentially, not in parallel

**File System Issues:**

*Problem*: Permission errors or file proliferation
*Solutions*:
- Ensure write permissions to experiments/ directory
- Use `archive` command regularly to clean up
- Don't create custom experiment files - use templates
- Check disk space availability
- Use `cleanup --dry-run` to preview cleanup actions

**Results and Metrics:**

*Problem*: Inconsistent or unrealistic results
*Solutions*:
- Validate term encoder roundtrip accuracy first
- Check rule encoders actually modify patterns (non-zero change)
- Review test data for bias or artifacts
- Compare against baseline implementations
- Use multiple small experiments rather than one large one
# ASR v2.0 Quick Reference: All Architecture Decisions

## Phase 1 ADRs (Implemented ✓)
- **ADR-11**: Feature-Based Hybrid Architecture
- **ADR-12**: Prompts as YAML Data
- **ADR-13**: Model Registry from .env
- **ADR-14**: No Backward Compatibility
- **ADR-15**: Standard Response Format
- **ADR-16**: Substrate-Level Workflow Navigation
- **ADR-17**: Self-Documenting Servers
- **ADR-18**: Single Docker Image Architecture

## Phase 2 ADRs (AKAB-Specific)
- **ADR-19**: Stateful Feature Management
- **ADR-20**: Multi-Turn Conversation Handling
- **ADR-21**: Cross-Feature Integration
- **ADR-22**: Complex Response Building
- **ADR-23**: Feature-Specific Utilities
- **ADR-24**: Execution Engine Pattern
- **ADR-25**: Progressive Loading Strategy
- **ADR-26**: Isolated Data Directory Pattern ⚠️ CRITICAL
- **ADR-27**: Model Registry Migration ⚠️ BREAKING
- **ADR-28**: Triple-Blinding Architecture
- **ADR-29**: Multi-Turn State Machine
- **ADR-30**: Provider Fail-Loud Pattern
- **ADR-31**: Archival and Unlocking System
- **ADR-32**: Cost Tracking Architecture
- **ADR-33**: Scientific Research Integrity Protocol ⚠️ CRITICAL

## Phase 3 ADRs (Synapse - TBD)
- To be defined during Synapse analysis

## Critical ADRs Requiring Special Attention

### ADR-26: Isolated Data Directory
- `/krill/` must be outside LLM allowed directories
- Essential for triple-blinding integrity
- No compromise possible

### ADR-27: Model Registry Migration
- Breaking change from hardcoded models
- Must use substrate ModelRegistry
- Update all model references

### ADR-33: Scientific Research Integrity
- Truth over helpfulness is mandatory
- Pre-registration of metrics required
- Nuclear honesty in reporting
- No p-hacking or bias allowed

## Usage
Each ADR is fully documented in the main ASR v2.0 document with:
- Context explaining the problem
- Decision stating the solution
- Implementation examples
- Consequences (positive and negative)

# BQX ML V3 Intelligence System

This directory contains the comprehensive knowledge base for the BQX ML V3 project in structured JSON format.

## Purpose

These intelligence files serve as the **definitive source of truth** for:
- Project context and infrastructure
- Terminology and semantic meaning
- System architecture and entity relationships
- Development protocols and workflows
- Constraints and requirements
- User mandates and critical rules

## Files

### 1. `context.json` - Project Context
- **Purpose**: High-level project overview and infrastructure details
- **Contents**: Project metadata, paradigm details, currency pairs, team info, current phase
- **Use Cases**: Understanding project scope, infrastructure setup, team roles

### 2. `semantics.json` - Terminology & Concepts
- **Purpose**: Definitions of all key terms and concepts
- **Contents**: Core concepts (BQX, Interval-Centric, etc.), feature categories, model types
- **Use Cases**: Clarifying terminology, understanding feature engineering, model architecture

### 3. `ontology.json` - Entity Relationships
- **Purpose**: Data model and entity relationship mapping
- **Contents**: Entity definitions, relationships, data flow, storage hierarchy
- **Use Cases**: Database schema understanding, entity modeling, data pipeline design

### 4. `protocols.json` - Development Procedures
- **Purpose**: Standard operating procedures for development and operations
- **Contents**: Git workflow, testing protocols, deployment procedures, security practices
- **Use Cases**: Development guidelines, operational procedures, security protocols

### 5. `constraints.json` - Architectural Constraints
- **Purpose**: Technical and business constraints that must be followed
- **Contents**: Architectural mandates, data quality requirements, performance limits, naming conventions
- **Use Cases**: Validation rules, performance benchmarking, compliance checking

### 6. `workflows.json` - Process Workflows
- **Purpose**: End-to-end process documentation
- **Contents**: Data ingestion, feature engineering, model training, prediction, deployment workflows
- **Use Cases**: Understanding pipelines, debugging processes, optimization opportunities

### 7. `mandates.json` - User Mandates
- **Purpose**: Critical requirements and mandates from users/stakeholders
- **Contents**: Critical mandates (BQX paradigm, interval-centric, model isolation), operational requirements
- **Use Cases**: Compliance verification, requirement validation, paradigm understanding

### 8. `metadata.json` - System Metadata
- **Purpose**: Intelligence system metadata and references
- **Contents**: Version info, project stats, repository metadata, references to key documents
- **Use Cases**: System information, documentation navigation, version tracking

## Usage

### For Developers
- Read `semantics.json` to understand terminology
- Reference `protocols.json` for development workflow
- Check `constraints.json` for validation rules
- Follow `mandates.json` for critical requirements

### For ML Engineers
- Study `ontology.json` for data model
- Review `workflows.json` for pipeline understanding
- Reference `semantics.json` for feature definitions
- Follow `mandates.json` for modeling constraints

### For Operations
- Check `protocols.json` for deployment procedures
- Monitor against `constraints.json` performance limits
- Follow `workflows.json` for operational processes
- Reference `context.json` for infrastructure details

### For AI Assistants (Claude Code)
- Load all intelligence files for comprehensive context
- Reference `mandates.json` for critical rules
- Use `semantics.json` for accurate terminology
- Follow `protocols.json` for code generation

## Maintenance

### Update Frequency
- `context.json`: On infrastructure or team changes
- `semantics.json`: When adding new concepts/features
- `ontology.json`: On data model changes
- `protocols.json`: When procedures change
- `constraints.json`: When requirements change
- `workflows.json`: On process updates
- `mandates.json`: When user requirements change
- `metadata.json`: On each intelligence system update

### Validation
All intelligence files should be:
- Valid JSON format
- Consistent across files
- Up-to-date with current implementation
- Reviewed during code reviews

## Integration

These intelligence files are:
- Referenced by Claude Code for context
- Used by documentation generators
- Validated in CI/CD pipelines
- Synced with AirTable project plan

## Version

- **Version**: 2.0.0
- **Created**: 2025-11-25
- **Last Updated**: 2025-12-08
- **Total Files**: 14
- **Total Size**: ~75 KB

## Current Status (2025-12-08)

- **V2 Migration**: IN PROGRESS (~62% complete)
- **Total Models**: 672 (28 pairs × 6 horizons × 4 ensemble)
- **Target Accuracy**: 95%+ (deploy farthest horizon achieving this)
- **Monthly Cost**: ~$277 (optimized)
- **Active Plan**: `/home/micha/.claude/plans/gentle-skipping-wirth.md`

## Links

- Main README: [/README.md](../README.md)
- Project Documentation: [/docs](../docs/)
- Scripts: [/scripts](../scripts/)
- Source Code: [/src](../src/)

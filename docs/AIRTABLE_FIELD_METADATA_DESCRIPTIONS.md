# AirTable Field Metadata Descriptions

**Purpose**: Standardized field descriptions for all ID fields in the BQX ML V3 AirTable base
**Date**: 2025-11-25
**Status**: Reference Guide for AirTable Configuration

---

## 📋 Overview

This document defines the standardized metadata descriptions for all ID fields in the AirTable base. These descriptions should be added to the respective fields in AirTable to ensure consistency and clarity.

### Standardized ID Format

| Entity | Field Name | Format | Example |
|--------|-----------|---------|---------|
| Plans | `plan_id` | `MP##` | MP03 |
| Phases | `phase_id` | `MP##.P##` | MP03.P02 |
| Stages | `stage_id` | `MP##.P##.S##` | MP03.P02.S07 |
| Tasks | `task_id` | `MP##.P##.S##.T##` | MP03.P02.S07.T01 |

---

## 🗂️ Plans Table

### Field: `plan_id`

**Field Type**: Single line text
**Required**: Yes
**Unique**: Yes

**Description**:
```
Master Plan Identifier in format MP##

Format: MP## (e.g., MP03)
- MP = Master Plan prefix
- ## = Two-digit plan number (01-99)

Standardized on 2025-11-25 to ensure hierarchical consistency across all entities.

Examples:
- MP01 = BQX ML v1
- MP03 = BQX ML v3: 28 Independent Models

This ID is referenced by all phases, stages, and tasks within the plan.
```

---

## 📊 Phases Table

### Field: `phase_id`

**Field Type**: Single line text
**Required**: Yes
**Unique**: Yes

**Description**:
```
Phase Identifier in hierarchical format MP##.P##

Format: MP##.P## (e.g., MP03.P02)
- MP## = Master Plan number
- P## = Phase number within the plan (01-99)

Standardized on 2025-11-25 to ensure hierarchical consistency.

Examples:
- MP03.P01 = Foundation and Setup (Plan MP03, Phase 01)
- MP03.P02 = Intelligence Architecture (Plan MP03, Phase 02)
- MP03.P08 = Model Training (Plan MP03, Phase 08)

This hierarchical format makes it clear which plan each phase belongs to and enables easy filtering and sorting.
```

**Additional Metadata**:
- **Validation Rule**: Must match pattern `MP\d{2}\.P\d{2}`
- **Display**: Show in all views with plan context

---

## 🎯 Stages Table

### Field: `stage_id`

**Field Type**: Single line text
**Required**: Yes
**Unique**: Yes

**Description**:
```
Stage Identifier in hierarchical format MP##.P##.S##

Format: MP##.P##.S## (e.g., MP03.P02.S07)
- MP## = Master Plan number
- P## = Phase number
- S## = Stage number within the phase (01-99)

Standardized on 2025-11-25 to ensure hierarchical consistency.

Examples:
- MP03.P02.S05 = Create 7 Intelligence JSON Files (Plan MP03, Phase 02, Stage 05)
- MP03.P02.S07 = Implement Intelligence File Update Hooks (Plan MP03, Phase 02, Stage 07)
- MP03.P08.S06 = Implement All 5 Model Algorithms (Plan MP03, Phase 08, Stage 06)

This hierarchical format clearly shows the plan → phase → stage relationship and enables:
- Easy filtering by plan or phase
- Logical ordering and sequencing
- Clear dependency tracking
- Automated validation of stage placement
```

**Additional Metadata**:
- **Validation Rule**: Must match pattern `MP\d{2}\.P\d{2}\.S\d{2}`
- **Display**: Show full hierarchy in views
- **Indexing**: Create index for fast lookups

---

## ✅ Tasks Table

### Field: `task_id`

**Field Type**: Single line text
**Required**: Yes
**Unique**: Yes

**Description**:
```
Task Identifier in hierarchical format MP##.P##.S##.T##

Format: MP##.P##.S##.T## (e.g., MP03.P02.S07.T01)
- MP## = Master Plan number
- P## = Phase number
- S## = Stage number
- T## = Task number within the stage (01-99)

Standardized on 2025-11-25 to ensure hierarchical consistency.

Examples:
- MP03.P01.S04.T01 = Install VS Code with Extensions (Plan MP03, Phase 01, Stage 04, Task 01)
- MP03.P02.S07.T04 = Configure CI/CD Validation Workflow (Plan MP03, Phase 02, Stage 07, Task 04)
- MP03.P08.S06.T12 = Test LSTM Model Performance (Plan MP03, Phase 08, Stage 06, Task 12)

This hierarchical format provides complete traceability:
- Plan MP03 (BQX ML V3)
  - Phase P02 (Intelligence Architecture)
    - Stage S07 (Intelligence File Update Hooks)
      - Task T04 (CI/CD Validation)

Benefits:
- Complete lineage from plan to task
- Easy dependency mapping
- Automated validation of task placement
- Clear progress tracking at all levels
- Simplified reporting and analytics
```

**Additional Metadata**:
- **Validation Rule**: Must match pattern `MP\d{2}\.P\d{2}\.S\d{2}\.T\d{2}`
- **Display**: Show full hierarchy with color coding by plan
- **Indexing**: Create composite index for performance

---

## 🔗 Relationship Fields

### Plans Table → Phases Table

**Field**: `phase_link`
**Type**: Link to Phases table

**Description**:
```
Links to all phases within this master plan.

Automatically populated based on matching plan_id prefix in phase_id field.
Example: Plan MP03 links to all phases with phase_id starting with "MP03."
```

### Phases Table → Stages Table

**Field**: `stage_link`
**Type**: Link to Stages table

**Description**:
```
Links to all stages within this phase.

Automatically populated based on matching plan and phase prefix in stage_id field.
Example: Phase MP03.P02 links to all stages with stage_id starting with "MP03.P02."
```

### Stages Table → Tasks Table

**Field**: `task_link`
**Type**: Link to Tasks table

**Description**:
```
Links to all tasks within this stage.

Automatically populated based on matching plan, phase, and stage prefix in task_id field.
Example: Stage MP03.P02.S07 links to all tasks with task_id starting with "MP03.P02.S07."
```

---

## 📐 Validation Rules

### ID Format Validation

All ID fields should have validation rules to ensure correct formatting:

```javascript
// Plans.plan_id validation
REGEX_MATCH({plan_id}, '^MP\\d{2}$')

// Phases.phase_id validation
REGEX_MATCH({phase_id}, '^MP\\d{2}\\.P\\d{2}$')

// Stages.stage_id validation
REGEX_MATCH({stage_id}, '^MP\\d{2}\\.P\\d{2}\\.S\\d{2}$')

// Tasks.task_id validation
REGEX_MATCH({task_id}, '^MP\\d{2}\\.P\\d{2}\\.S\\d{2}\\.T\\d{2}$')
```

### Hierarchical Consistency Validation

Ensure child entities reference valid parent entities:

```javascript
// Phase must belong to existing plan
LEFT({phase_id}, 4) = {plan_id}

// Stage must belong to existing phase
LEFT({stage_id}, 7) = {phase_id}

// Task must belong to existing stage
LEFT({task_id}, 10) = {stage_id}
```

---

## 🎨 Display Configuration

### Color Coding by Plan

Apply color coding to visually distinguish different plans:

| Plan | Color | Hex Code |
|------|-------|----------|
| MP01 | Blue | #2196F3 |
| MP03 | Green | #4CAF50 |
| MP04 | Orange | #FF9800 |
| MP05 | Purple | #9C27B0 |

### View Grouping

Configure views to group by hierarchy levels:

1. **Plan View**: Group by `plan_id`
2. **Phase View**: Group by `phase_id` (first 7 characters)
3. **Stage View**: Group by `stage_id` (first 10 characters)
4. **Task View**: Show full hierarchy with indentation

---

## 📊 Reporting and Analytics

### Useful Formula Fields

**Extract Plan from any ID**:
```javascript
// For phase_id, stage_id, or task_id
LEFT({id_field}, 4)
```

**Extract Phase from Stage or Task ID**:
```javascript
LEFT({id_field}, 7)
```

**Extract Stage from Task ID**:
```javascript
LEFT({id_field}, 10)
```

**Count Phases per Plan**:
```javascript
COUNTALL({phase_link})
```

**Count Stages per Phase**:
```javascript
COUNTALL({stage_link})
```

**Count Tasks per Stage**:
```javascript
COUNTALL({task_link})
```

---

## 🛠️ Implementation Checklist

### Plans Table
- [ ] Update `plan_id` field description
- [ ] Add validation rule for MP## format
- [ ] Configure color coding
- [ ] Set up plan view with grouping

### Phases Table
- [ ] Update `phase_id` field description
- [ ] Add validation rule for MP##.P## format
- [ ] Add hierarchical consistency check
- [ ] Configure color coding by plan
- [ ] Set up phase view with grouping

### Stages Table
- [ ] Update `stage_id` field description
- [ ] Add validation rule for MP##.P##.S## format
- [ ] Add hierarchical consistency check
- [ ] Configure color coding by plan
- [ ] Set up stage view with hierarchy

### Tasks Table
- [ ] Update `task_id` field description
- [ ] Add validation rule for MP##.P##.S##.T## format
- [ ] Add hierarchical consistency check
- [ ] Configure color coding by plan
- [ ] Set up task view with full hierarchy

---

## 📝 Migration Notes

**Date Standardized**: 2025-11-25

**Changes Applied**:
1. Plans: P## → MP##
2. Phases: P##.## → MP##.P##
3. Stages: S##.##.## → MP##.P##.S##
4. Tasks: T##.##.##.## → MP##.P##.S##.T##

**Files Updated**:
- AirTable Plans, Phases, Stages, Tasks tables
- Intelligence JSON files (context.json, metadata.json)
- All documentation files (22 markdown files)
- README files
- Scripts and configurations

**Mapping Files**:
- `airtable_id_mappings.json` (phases, stages, tasks)
- `plan_id_mappings.json` (plans)

---

## 🔍 Quality Assurance

### Verification Queries

**Check all IDs follow new format**:
```javascript
// Plans
REGEX_MATCH({plan_id}, '^MP\\d{2}$')

// Phases
REGEX_MATCH({phase_id}, '^MP\\d{2}\\.P\\d{2}$')

// Stages
REGEX_MATCH({stage_id}, '^MP\\d{2}\\.P\\d{2}\\.S\\d{2}$')

// Tasks
REGEX_MATCH({task_id}, '^MP\\d{2}\\.P\\d{2}\\.S\\d{2}\\.T\\d{2}$')
```

**Check hierarchical consistency**:
```javascript
// All phases must have valid plan
FIND({plan_id}, {phase_id}) = 1

// All stages must have valid phase
FIND({phase_id}, {stage_id}) = 1

// All tasks must have valid stage
FIND({stage_id}, {task_id}) = 1
```

---

## 📚 Related Documentation

- [AirTable Project Management Protocol](AIRTABLE_PROJECT_MANAGEMENT_PROTOCOL.md)
- [Project Plan 100% Complete](PROJECT_PLAN_100_PERCENT_COMPLETE.md)
- [BQX ML V3 Intelligence Architecture Guide](BQX_ML_V3_INTELLIGENCE_ARCHITECTURE_GUIDE.md)

---

*Document Version: 1.0*
*Created: 2025-11-25*
*Author: BQXML Chief Engineer*

# AirTable BQX-ML Base Structure

**Base ID**: appR3PPnrNkVo48mO

## Table: Plans
**ID**: tblTtBE4sEa5ibCHE

**Description**: Strategic-level view of all major projects in the Robkei ecosystem. Each project represents a significant initiative with defined timeline, budget, objectives, and success criteria. Projects contain phases which break down the work into manageable chunks.

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| plan_id | singleLineText | Unique plan identifier using hierarchical format. Format: P## (e.g., MP01, P02). Sequential numbering for each plan. Example: MP01 |
| name | singleLineText | Concise, actionable title describing WHAT needs to be done. Write 5-10 word action-oriented title. Start with verb. Be specific. Example: Configure BigQuery Dataset for EUR/USD Data |
| description | richText | Detailed explanation of WHY this matters, HOW to approach it, and success criteria. Include: 1) Context and objectives, 2) Technical approach, 3) Success metrics. Use 2-5 sentences. Example: Set up partitioned BigQuery tables for EUR/USD 1-minute OHLCV data. Configure daily partitioning on timestamp field for query efficiency. Success: Tables created with proper schemas, <100ms query performance. |
| status | singleSelect | Current execution status of the work item. Select from: Not Started | In Progress | Completed | Blocked | Cancelled Example: In Progress |
| owner | singleLineText | Person or team responsible for overall delivery. Use consistent naming: Team name or individual email/ID Example: ML Team |
| duration | singleLineText | Estimated duration. Format: #w (weeks) or #d (days) |
| budget | number | Budget allocation in USD. Format: #####.## |
| realized_cost | number | Actual cost incurred in USD. Format: #####.## |
| notes | multilineText | Living documentation capturing decisions, blockers, learnings, and progress updates. Document journey not destination. Include: decisions made, trade-offs, current blockers, lessons learned, links to discussions, warnings/gotchas, stakeholder feedback. Format: Date-stamped entries for traceability. Example: 2025-11-20: Chose BigQuery clustering over partitioning after testing showed 3x improvement. Blocked by GCP quota (ticket #123). DevOps recommends hourly partitions. Design doc: docs.google.com/... 2025-11-22: Unblocked - quota increased. Implementing hourly partitions as suggested. |
| attachments | multipleAttachments | Related files and documents. Upload supporting materials here. |
| parent_plan | singleLineText | ID of parent plan for hierarchical planning. Format: ## |
| depends_on_plans | multipleRecordLinks | Plans this Plan depends on (must complete before this Plan starts) |
| blocks_plans | multipleRecordLinks |  |
| phases | multipleRecordLinks |  |
| stages | multipleRecordLinks |  |
| tasks | multipleRecordLinks |  |
| source | multilineText | Source files from workspace that contributed content to this record |

---

## Table: Phases
**ID**: tblbNORPGr9fcOnsP

**Description**: Tactical-level breakdown of projects into major phases. Each phase has specific objectives, deliverables, and timeline. Phases contain stages (sub-phases) and roll up progress from those stages. Dependencies between phases can be tracked.

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| phase_id | singleLineText | Unique phase identifier with plan reference. Format: P##.## (e.g., MP01.01). First part is plan, second is phase number. Example: MP01.03 |
| status | singleSelect | Current execution status of the work item. Select from: Not Started | In Progress | Completed | Blocked | Cancelled Example: In Progress |
| name | singleLineText | Concise, actionable title describing WHAT needs to be done. Write 5-10 word action-oriented title. Start with verb. Be specific. Example: Configure BigQuery Dataset for EUR/USD Data |
| description | richText | Detailed explanation of WHY this matters, HOW to approach it, and success criteria. Include: 1) Context and objectives, 2) Technical approach, 3) Success metrics. Use 2-5 sentences. Example: Set up partitioned BigQuery tables for EUR/USD 1-minute OHLCV data. Configure daily partitioning on timestamp field for query efficiency. Success: Tables created with proper schemas, <100ms query performance. |
| notes | multilineText | Living documentation capturing decisions, blockers, learnings, and progress updates. Document journey not destination. Include: decisions made, trade-offs, current blockers, lessons learned, links to discussions, warnings/gotchas, stakeholder feedback. Format: Date-stamped entries for traceability. Example: 2025-11-20: Chose BigQuery clustering over partitioning after testing showed 3x improvement. Blocked by GCP quota (ticket #123). DevOps recommends hourly partitions. Design doc: docs.google.com/... 2025-11-22: Unblocked - quota increased. Implementing hourly partitions as suggested. |
| milestones | richText |  |
| deliverables | richText |  |
| duration | singleLineText | Estimated duration. Format: #w (weeks) or #d (days) |
| owner | singleLineText | Person or team responsible for overall delivery. Use consistent naming: Team name or individual email/ID Example: ML Team |
| estimated_budget | number | Estimated budget in USD. Format: #####.## |
| realized_cost | number | Actual cost incurred in USD. Format: #####.## |
| source | multilineText | Source files from workspace that contributed content to this record |
| attachments | multipleAttachments | Related files and documents. Upload supporting materials here. |
| plan_link | multipleRecordLinks | Link to parent plan record |
| predecessor | singleLineText | Predecessor phase ID (##.##) |
| stage_link | multipleRecordLinks |  |
| task_link | multipleRecordLinks |  |
| record_audit | aiText |  |
| record_score | number |  |

---

## Table: Stages
**ID**: tblxnuvF8O7yH1dB4

**Description**: Operational-level sub-phases within each phase (e.g., Phase 1a, 1b, 1c). Each stage represents a cohesive unit of work with clear charge (directive) and outcome (deliverables). Stages contain individual tasks and define autonomy levels.

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| stage_id | singleLineText | Unique stage identifier with phase reference. Format: S##.## (e.g., S02.15). Maps to specific work stream. Example: S02.30 |
| status | singleSelect | Current execution status of the work item. Select from: Not Started | In Progress | Completed | Blocked | Cancelled Example: In Progress |
| name | singleLineText | Concise, actionable title describing WHAT needs to be done. Write 5-10 word action-oriented title. Start with verb. Be specific. Example: Configure BigQuery Dataset for EUR/USD Data |
| description | richText | Detailed explanation of WHY this matters, HOW to approach it, and success criteria. Include: 1) Context and objectives, 2) Technical approach, 3) Success metrics. Use 2-5 sentences. Example: Set up partitioned BigQuery tables for EUR/USD 1-minute OHLCV data. Configure daily partitioning on timestamp field for query efficiency. Success: Tables created with proper schemas, <100ms query performance. |
| notes | multilineText | Living documentation capturing decisions, blockers, learnings, and progress updates. Document journey not destination. Include: decisions made, trade-offs, current blockers, lessons learned, links to discussions, warnings/gotchas, stakeholder feedback. Format: Date-stamped entries for traceability. Example: 2025-11-20: Chose BigQuery clustering over partitioning after testing showed 3x improvement. Blocked by GCP quota (ticket #123). DevOps recommends hourly partitions. Design doc: docs.google.com/... 2025-11-22: Unblocked - quota increased. Implementing hourly partitions as suggested. |
| realized_cost | number | Actual cost incurred in USD. Format: #####.## |
| plan_link | multipleRecordLinks | Link to parent plan record |
| phase_link | multipleRecordLinks |  |
| task_link | multipleRecordLinks |  |
| blocked_by | singleLineText | ID of blocking stage/task |
| attachments | multipleAttachments | Related files and documents. Upload supporting materials here. |
| source | multilineText | Source files from workspace that contributed content to this record |
| record_audit | aiText |  |
| record_score | number |  |

---

## Table: Tasks
**ID**: tblQ9VXdTgZiIR6H2

**Description**: Execution-level individual actionable tasks with complete metadata. Each task has detailed charge (instructions), outcome (success criteria), cost tracking, resource requirements, dependencies, and knowledge capture. This is where work actually gets done.

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| task_id | singleLineText | Unique task identifier with full hierarchy. Format: T##.##.## (e.g., T02.30.01). Shows phase.stage.task structure. Example: T02.30.05 |
| status | singleSelect | Current execution status of the work item. Select from: Not Started | In Progress | Completed | Blocked | Cancelled Example: In Progress |
| priority | singleSelect | Relative importance and urgency of the item. Select from: Critical | High | Medium | Low. Consider dependencies and deadlines. Example: High |
| name | singleLineText | Concise, actionable title describing WHAT needs to be done. Write 5-10 word action-oriented title. Start with verb. Be specific. Example: Configure BigQuery Dataset for EUR/USD Data |
| description | richText | Detailed explanation of WHY this matters, HOW to approach it, and success criteria. Include: 1) Context and objectives, 2) Technical approach, 3) Success metrics. Use 2-5 sentences. Example: Set up partitioned BigQuery tables for EUR/USD 1-minute OHLCV data. Configure daily partitioning on timestamp field for query efficiency. Success: Tables created with proper schemas, <100ms query performance. |
| notes | multilineText | Living documentation capturing decisions, blockers, learnings, and progress updates. Document journey not destination. Include: decisions made, trade-offs, current blockers, lessons learned, links to discussions, warnings/gotchas, stakeholder feedback. Format: Date-stamped entries for traceability. Example: 2025-11-20: Chose BigQuery clustering over partitioning after testing showed 3x improvement. Blocked by GCP quota (ticket #123). DevOps recommends hourly partitions. Design doc: docs.google.com/... 2025-11-22: Unblocked - quota increased. Implementing hourly partitions as suggested. |
| assigned_to | singleLineText | Individual currently working on this task. Use email or employee ID for consistency Example: john.smith@company.com |
| stage_link | multipleRecordLinks |  |
| attachments | multipleAttachments | Related files and documents. Upload supporting materials here. |
| source | multilineText | Source files from workspace that contributed content to this record |
| record_audit | aiText |  |
| record_score | number |  |
| ABCX | singleSelect |  |
| estimated_hours | number | Estimated effort in hours to complete. Use realistic estimates. Include testing and documentation time. Example: 8 |
| actual_hours | number | Actual hours spent (for tracking and improvement). Track actual time for better future estimates Example: 10.5 |
| realized_cost | number | Actual cost incurred in USD. Format: #####.## |
| artifacts | multilineText | Deliverables and outputs produced. List files, models, or documentation created Example: bigquery_schema.sql, data_pipeline.py, architecture.md |
| plan_link | multipleRecordLinks | Link to parent plan record |
| phase_link | multipleRecordLinks |  |
| epic_id | singleLineText | Epic ID for grouping (E-###) |
| tags | multipleSelects | Categorization labels for filtering and grouping. Select multiple: development, testing, ml, infrastructure, etc. Example: ml, feature-engineering, bigquery |
| blockers | multilineText | Current impediments preventing progress. Clearly describe what is blocking and what is needed to unblock Example: Waiting for GCP quota increase approval (ticket #12345) |

---


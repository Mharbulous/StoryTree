# Planning Stage

> For definitions of stages, holds, and dispositions, see @workflow-three-field-model.md

---

## Stage Diagram

```mermaid
flowchart TB
    concept[concept: approved] -->|approved| p_clear

    subgraph planning_stage [planning]
        p_clear[no hold]
        p_create((AI creates))
        p_review((AI reviews))
        p_blocked[blocked]
        p_create_deps((AI creates<br/>dep stories))
        p_queued[queued]
        p_polish[polish]
        p_refine((AI refines))

        p_clear --> p_create
        p_create --> p_review
        p_review -->|3rd-party deps| p_blocked
        p_review -->|pre-requisites| p_queued
        p_blocked --> p_create_deps
        p_create_deps -->|child stories<br/>reach planning| p_queued
        p_queued -->|pre-reqs met| p_polish
        p_polish --> p_refine
        p_refine --> p_review
    end

    p_review -->|no blockers| executing[executing: no hold]

    classDef conceptBox fill:#66CC00,stroke:#52A300,color:#fff
    classDef planningBox fill:#00CC66,stroke:#00A352,color:#fff
    classDef executingBox fill:#00CCCC,stroke:#00A3A3,color:#fff
    class concept conceptBox
    class planning_stage planningBox
    class executing executingBox
```

---

## Workflow Description

### Entry
Stories enter planning with **no hold** after human approval in concept stage.

### AI Create Phase
AI creates TDD implementation plan:

1. **Research codebase** - Understand existing architecture, patterns, and conventions
2. **Draft TDD plan** - Write test scenarios first, then implementation steps
3. **Generate plan file** - Output structured plan with file paths and code examples

### AI Review Phase
AI reviews the plan for dependency issues:

1. **Check third-party dependencies** - Does this plan require libraries, APIs, or external services not yet available?
2. **Check pre-requisite stories** - Does this plan depend on other stories being implemented first?

### AI Creates Dependency Stories Phase
When a story is blocked due to third-party dependencies:

1. **Create child stories** - AI creates child story-nodes for installing/configuring each 3rd-party dependency
2. **Document requirements** - Each child story captures the specific dependency installation steps
3. **Convert to pre-requisites** - Once all child stories reach planning stage, the dependency is no longer "third-party" but a documented pre-requisite story

This transforms external blockers into internal, trackable work items.

### Hold Outcomes

| Hold | Trigger | Resolution |
|------|---------|------------|
| **blocked** | Third-party dependencies (libraries, APIs, external services) | AI creates child stories for each dependency; when all child stories reach `planning` stage, story moves to `queued` |
| **queued** | Pre-requisite stories identified (or converted from blocked) | Automatic—when all pre-requisite stories reach `implemented` or later, story moves to `polish` |
| **polish** | Pre-requisites satisfied | AI refines plan to incorporate completed pre-requisites, then re-reviews |

### Exit
When AI review finds no blockers → story moves to executing stage with **no hold**.

# Story Tree Workflow Diagrams

This document provides visual representations of the key workflows and data structures used by the story-tree skill system.

**Document structure:** Conceptual model → Data storage → Operational workflows

---

## Table of Contents

1. [Definitions](#definitions)
2. [Three-Field Workflow Model](#three-field-workflow-model)
   - Stage Transitions
   - Multi-Faceted Stage Meanings
   - Hold States
   - Disposition States
3. [Database Architecture](#database-architecture)
   - Closure Table Data Structure
   - Closure Table Path Example
   - Node Insertion Process
   - Dynamic Capacity Calculation
4. [Skill Workflows](#skill-workflows)
   - Main Update Workflow
   - Priority Algorithm Decision Flow
   - Git Commit Analysis Process
   - Story Generation Flow

---

## Definitions

| Term | Definition |
|------|------------|
| **Story node** | A unit of work in the hierarchical backlog—can be an epic, feature, capability, or task depending on depth. May have its own direct work AND children simultaneously. |
| **Closure table** | A database pattern that stores all ancestor-descendant relationships, enabling efficient hierarchy queries |
| **Capacity** | The maximum number of children a node can have; grows dynamically based on completed work |
| **Depth** | A node's level in the tree (root=0, features=1, capabilities=2, tasks=3+) |
| **Fill rate** | Ratio of current children to capacity; used for prioritization |
| **Checkpoint** | The last analyzed git commit hash; enables incremental scanning |

---

## Three-Field Workflow Model

Stories progress through stages, with holds and dispositions as orthogonal states:

### Stage

```mermaid
flowchart TB
    root((Stories))

    concept[concept]
    concept_desc[New idea proposed]

    planning[planning]
    planning_desc[Implementation being planned; dependencies being verified]

    executing[executing]
    executing_desc[Own code in progress; children's code in progress]

    reviewing[reviewing]
    reviewing_desc[Own code under review; reviewing child code]

    verifying[verifying]
    verifying_desc[Own implementation being tested; verifying integration with children]

    implemented[implemented]
    implemented_desc[Own code complete; all children implemented and integrated]

    ready[ready]
    ready_desc[Own work fully tested; entire subtree fully tested]

    released[released]
    released_desc[Shipped]

    root --> concept --> concept_desc
    root --> planning --> planning_desc
    root --> executing --> executing_desc
    root --> reviewing --> reviewing_desc
    root --> verifying --> verifying_desc
    root --> implemented --> implemented_desc
    root --> ready --> ready_desc
    root --> released --> released_desc

    classDef rootStyle fill:#888888,stroke:#666,color:#fff
    classDef conceptStyle fill:#66CC00,stroke:#52A300,color:#fff
    classDef planningStyle fill:#00CC66,stroke:#00A352,color:#fff
    classDef executingStyle fill:#00CCCC,stroke:#00A3A3,color:#fff
    classDef reviewingStyle fill:#0099CC,stroke:#007AA3,color:#fff
    classDef verifyingStyle fill:#0066CC,stroke:#0052A3,color:#fff
    classDef implementedStyle fill:#0033CC,stroke:#0029A3,color:#fff
    classDef readyStyle fill:#0000CC,stroke:#0000A3,color:#fff
    classDef releasedStyle fill:#3300CC,stroke:#2900A3,color:#fff

    class root rootStyle
    class concept conceptStyle
    class planning planningStyle
    class executing executingStyle
    class reviewing reviewingStyle
    class verifying verifyingStyle
    class implemented implementedStyle
    class ready readyStyle
    class released releasedStyle
```

### Hold Status

```mermaid
flowchart TB
    root((No hold))

    broken[🔥 broken]
    broken_desc[Implementation has issues]

    conflicted[⚔ conflicted]
    conflicted_desc[Scope overlaps another story]

    blocked[🚧 blocked]
    blocked_desc[External dependency missing]
    blocked_not[Not a choice to stop]

    escalated[⏳ escalated]
    escalated_desc[Requires human decision]

    paused[⏸ paused]
    paused_desc[Intentionally stopped]
    paused_not[Not blocked by external factors]

    polish[💎 polish]
    polish_desc[Minor refinements before progressing]

    queued[📋 queued]
    queued_desc[Awaiting automated processing]

    wishlisted[💭 wishlisted]
    wishlisted_desc[Low priority, indefinite deferral]

    root --> broken --> broken_desc
    root --> conflicted --> conflicted_desc
    root --> blocked --> blocked_desc --> blocked_not
    root --> escalated --> escalated_desc
    root --> paused --> paused_desc --> paused_not
    root --> polish --> polish_desc
    root --> queued --> queued_desc
    root --> wishlisted --> wishlisted_desc

    classDef nohold fill:#888888,stroke:#666,color:#fff
    classDef brokenStyle fill:#CC4400,stroke:#AA3700,color:#fff
    classDef conflictedStyle fill:#D25B00,stroke:#B04D00,color:#fff
    classDef blockedStyle fill:#DB7100,stroke:#B95E00,color:#fff
    classDef escalatedStyle fill:#E28B00,stroke:#C07600,color:#000
    classDef pausedStyle fill:#E4A000,stroke:#C28800,color:#000
    classDef polishStyle fill:#E6B200,stroke:#C49600,color:#000
    classDef queuedStyle fill:#E8C200,stroke:#C6A300,color:#000
    classDef wishlistedStyle fill:#EAD000,stroke:#C8B100,color:#000

    class root nohold
    class broken,broken_desc brokenStyle
    class conflicted,conflicted_desc conflictedStyle
    class blocked,blocked_desc,blocked_not blockedStyle
    class escalated,escalated_desc escalatedStyle
    class paused,paused_desc,paused_not pausedStyle
    class polish,polish_desc polishStyle
    class queued,queued_desc queuedStyle
    class wishlisted,wishlisted_desc wishlistedStyle
```

### Disposition

```mermaid
flowchart TB
    root((Not disposed))

    infeasible[🚫 infeasible]
    infeasible_desc[Cannot be built]

    rejected[❌ rejected]
    rejected_desc[Explicitly declined]

    duplicative[👯 duplicative]
    duplicative_desc[Duplicate of another story]

    deprecated[⚠️ deprecated]
    deprecated_desc[No longer recommended]

    legacy[🛑 legacy]
    legacy_desc[Outdated or superseded]

    archived[📦 archived]
    archived_desc[Stored away for reference]

    root --> infeasible --> infeasible_desc
    root --> rejected --> rejected_desc
    root --> duplicative --> duplicative_desc
    root --> deprecated --> deprecated_desc
    root --> legacy --> legacy_desc
    root --> archived --> archived_desc

    classDef notDisposed fill:#9900CC,stroke:#7700AA,color:#fff
    classDef terminalStyle fill:#CC0000,stroke:#AA0000,color:#fff

    class root notDisposed
    class infeasible,infeasible_desc,rejected,rejected_desc,duplicative,duplicative_desc,deprecated,deprecated_desc,legacy,legacy_desc,archived,archived_desc terminalStyle
```

### Stage Transitions

Holds gate progression within each stage. Clearing all holds triggers automatic transition to the next stage's queue.

```mermaid
flowchart LR
    subgraph concept_stage [concept]
        c_q[📋 queued]
        c_e[⏳ escalated]
        c_h[other holds]
        c_clear((no hold))
        c_q --> c_e
        c_e --> c_clear
        c_q --> c_h
        c_h --> c_clear
    end

    subgraph planning_stage [planning]
        p_q[📋 queued]
        p_h[holds]
        p_clear((no hold))
        p_q --> p_h
        p_h --> p_clear
        p_q --> p_clear
    end

    subgraph executing_stage [executing]
        e_q[📋 queued]
        e_h[holds]
        e_clear((no hold))
        e_q --> e_h
        e_h --> e_clear
        e_q --> e_clear
    end

    subgraph review_stage [reviewing]
        r_q[📋 queued]
        r_h[holds]
        r_clear((no hold))
        r_q --> r_h
        r_h --> r_clear
        r_q --> r_clear
    end

    subgraph verify_stage [verifying]
        v_q[📋 queued]
        v_h[holds]
        v_clear((no hold))
        v_q --> v_h
        v_h --> v_clear
        v_q --> v_clear
    end

    subgraph impl_stage [implemented]
        i_q[📋 queued]
        i_h[holds]
        i_clear((no hold))
        i_q --> i_h
        i_h --> i_clear
        i_q --> i_clear
    end

    subgraph ready_stage [ready]
        rd_q[📋 queued]
        rd_h[holds]
        rd_clear((no hold))
        rd_q --> rd_h
        rd_h --> rd_clear
        rd_q --> rd_clear
    end

    subgraph released_stage [released]
        rel[✓ shipped]
    end

    c_clear -->|auto-queue| p_q
    p_clear -->|auto-queue| e_q
    e_clear -->|auto-queue| r_q
    r_clear -->|auto-queue| v_q
    v_clear -->|auto-queue| i_q
    i_clear -->|auto-queue| rd_q
    rd_clear -->|auto-queue| rel

    classDef conceptBox fill:#66CC00,stroke:#52A300,color:#fff
    classDef planningBox fill:#00CC66,stroke:#00A352,color:#fff
    classDef executingBox fill:#00CCCC,stroke:#00A3A3,color:#fff
    classDef reviewingBox fill:#0099CC,stroke:#007AA3,color:#fff
    classDef verifyingBox fill:#0066CC,stroke:#0052A3,color:#fff
    classDef implementedBox fill:#0033CC,stroke:#0029A3,color:#fff
    classDef readyBox fill:#0000CC,stroke:#0000A3,color:#fff
    classDef releasedBox fill:#3300CC,stroke:#2900A3,color:#fff
    classDef clearNode fill:#90EE90,stroke:#228B22,color:#000

    class concept_stage conceptBox
    class planning_stage planningBox
    class executing_stage executingBox
    class review_stage reviewingBox
    class verify_stage verifyingBox
    class impl_stage implementedBox
    class ready_stage readyBox
    class released_stage releasedBox
    class c_clear,p_clear,e_clear,r_clear,v_clear,i_clear,rd_clear clearNode
```

**Key principle:** "No hold" in any stage = ready to transition to the next stage's queue. The hold system is the universal gating mechanism.

---

## Database Architecture

### Closure Table Data Structure

The closure table pattern stores all ancestor-descendant relationships, enabling efficient hierarchy queries without recursion.

```mermaid
erDiagram
    story_nodes {
        text id PK
        text title
        text description
        int capacity
        text stage
        text hold_reason
        text disposition
        int human_review
        text project_path
        text last_implemented
        text created_at
        text updated_at
    }

    story_paths {
        text ancestor_id FK
        text descendant_id FK
        int depth
    }

    story_commits {
        text story_id FK
        text commit_hash PK
        text commit_date
        text commit_message
    }

    metadata {
        text key PK
        text value
    }

    story_nodes ||--o{ story_paths : "ancestor"
    story_nodes ||--o{ story_paths : "descendant"
    story_nodes ||--o{ story_commits : "linked"
```

### Closure Table Path Example

This diagram illustrates how the closure table stores paths for a simple three-node hierarchy.

```mermaid
flowchart TD
    subgraph Tree Structure
        ROOT[root] --> N1[1.1]
        N1 --> N2[1.1.1]
    end

    subgraph Closure Table Entries
        direction LR
        P1["(root, root, 0)"]
        P2["(root, 1.1, 1)"]
        P3["(root, 1.1.1, 2)"]
        P4["(1.1, 1.1, 0)"]
        P5["(1.1, 1.1.1, 1)"]
        P6["(1.1.1, 1.1.1, 0)"]
    end

    ROOT -.-> P1
    ROOT -.-> P2
    ROOT -.-> P3
    N1 -.-> P4
    N1 -.-> P5
    N2 -.-> P6
```

Each entry represents a path from ancestor to descendant with the distance between them. Self-references (depth 0) ensure every node appears in queries. This structure allows finding all descendants or ancestors with a single query.

### Node Insertion Process

Adding a new node requires updating both the nodes table and the closure table.

```mermaid
sequenceDiagram
    participant S as Skill
    participant N as story_nodes
    participant P as story_paths

    S->>N: INSERT new node (id, title, description, status)
    N-->>S: Node created

    S->>P: SELECT all paths where descendant = parent_id
    P-->>S: Return parent's ancestor paths

    S->>P: INSERT paths with new_id as descendant, depth + 1
    P-->>S: Ancestor paths copied

    S->>P: INSERT self-reference (new_id, new_id, 0)
    P-->>S: Self-reference added

    Note over S,P: Node is now fully integrated into tree hierarchy
```

### Dynamic Capacity Calculation

Capacity grows organically based on completed work rather than speculation.

```mermaid
flowchart LR
    subgraph Formula
        BASE[Base: 3] --> PLUS[+]
        PLUS --> IMPL[Count of implemented/ready children]
        IMPL --> RESULT[= Effective Capacity]
    end

    subgraph Example
        E1["New node: 3 + 0 = 3"]
        E2["1 child done: 3 + 1 = 4"]
        E3["3 children done: 3 + 3 = 6"]
    end

    RESULT --> E1
    RESULT --> E2
    RESULT --> E3
```

---

## Skill Workflows

### Main Update Workflow

The primary workflow executes when the skill receives an update command. It proceeds through seven sequential steps.

```mermaid
flowchart TD
    START([User invokes skill]) --> STALE{Database > 3 days old?}
    STALE -->|Yes| FORCE[Force full update first]
    FORCE --> STEP1
    STALE -->|No| STEP1

    STEP1[Step 1: Load Current Tree] --> DB_EXISTS{Database exists?}
    DB_EXISTS -->|No| INIT[Initialize new database]
    INIT --> SEED[Seed root node from project metadata]
    SEED --> STEP2
    DB_EXISTS -->|Yes| STEP2

    STEP2[Step 2: Analyze Git Commits] --> CHECKPOINT{Valid checkpoint exists?}
    CHECKPOINT -->|Yes| INCREMENTAL[Incremental scan from checkpoint]
    CHECKPOINT -->|No| FULL[Full 30-day scan]
    INCREMENTAL --> MATCH
    FULL --> MATCH
    MATCH[Match commits to stories] --> UPDATE_STATUS[Update story statuses]
    UPDATE_STATUS --> SAVE_CHECKPOINT[Save new checkpoint]
    SAVE_CHECKPOINT --> STEP3

    STEP3[Step 3: Calculate Tree Metrics] --> METRICS[Query depth, child count, fill rate per node]
    METRICS --> STEP4

    STEP4[Step 4: Identify Priority Target] --> FILTER[Filter eligible nodes]
    FILTER --> SORT[Sort by depth then fill rate]
    SORT --> SELECT[Select top priority node]
    SELECT --> STEP5

    STEP5[Step 5: Generate Stories] --> CONTEXT[Gather parent and sibling context]
    CONTEXT --> GENERATE[Generate 1-3 concept stories]
    GENERATE --> VALIDATE[Validate against quality checks]
    VALIDATE --> STEP6

    STEP6[Step 6: Update Tree] --> INSERT[Insert new nodes]
    INSERT --> CLOSURE[Populate closure table paths]
    CLOSURE --> TIMESTAMP[Update lastUpdated metadata]
    TIMESTAMP --> STEP7

    STEP7[Step 7: Output Report] --> REPORT([Generate summary report])
```

## Priority Algorithm Decision Flow

The priority algorithm determines which node should receive new children. Depth takes absolute precedence over fill rate.

```mermaid
flowchart TD
    START([Find priority target]) --> QUERY[Query all nodes]
    QUERY --> FILTER{Node eligible?}

    FILTER -->|stage = concept| SKIP[Skip this node]
    FILTER -->|hold_reason set| SKIP
    FILTER -->|disposition set| SKIP
    SKIP --> NEXT_NODE[Check next node]
    NEXT_NODE --> FILTER

    FILTER -->|stage != concept,<br/>no hold, no disposition| CAPACITY{Under capacity?}
    CAPACITY -->|No| SKIP
    CAPACITY -->|Yes| ADD[Add to candidates]
    ADD --> NEXT_NODE

    NEXT_NODE -->|No more nodes| SORT[Sort candidates]
    SORT --> DEPTH[Primary: Sort by depth ascending]
    DEPTH --> FILL[Secondary: Sort by fill rate ascending]
    FILL --> RESULT([Return first candidate])

    style RESULT fill:#90EE90
```

## Git Commit Analysis Process

The skill analyzes git history to detect implementation progress and update story statuses.

```mermaid
flowchart TD
    START([Begin git analysis]) --> GET_CHECKPOINT[Get lastAnalyzedCommit from metadata]
    GET_CHECKPOINT --> HAS_CHECKPOINT{Checkpoint exists?}

    HAS_CHECKPOINT -->|No| FULL_SCAN[Run: git log --since 30 days ago]
    HAS_CHECKPOINT -->|Yes| VALIDATE[Validate checkpoint in git history]

    VALIDATE --> VALID{Commit still exists?}
    VALID -->|No| LOG_REASON[Log: checkpoint rebased away]
    LOG_REASON --> FULL_SCAN
    VALID -->|Yes| INCREMENTAL[Run: git log checkpoint..HEAD]

    FULL_SCAN --> PARSE
    INCREMENTAL --> PARSE

    PARSE[Parse commit hash, date, message] --> FOREACH[For each commit]

    FOREACH --> EXTRACT[Extract keywords from message]
    EXTRACT --> QUERY_STORIES[Query non-deprecated stories]
    QUERY_STORIES --> COMPARE[Compare keywords via Jaccard similarity]

    COMPARE --> THRESHOLD{Similarity >= 0.7?}
    THRESHOLD -->|Yes| STRONG[Strong match: link and update status]
    THRESHOLD -->|No| WEAK{Similarity >= 0.4?}
    WEAK -->|Yes| POTENTIAL[Potential match: link only]
    WEAK -->|No| NO_MATCH[No match]

    STRONG --> NEXT_COMMIT
    POTENTIAL --> NEXT_COMMIT
    NO_MATCH --> NEXT_COMMIT

    NEXT_COMMIT[Process next commit] --> MORE{More commits?}
    MORE -->|Yes| FOREACH
    MORE -->|No| SAVE[Save newest commit as checkpoint]
    SAVE --> DONE([Analysis complete])
```

## Story Generation Flow

When a priority target is identified, the skill generates contextually appropriate stories.

```mermaid
flowchart TD
    START([Generate stories for target node]) --> GET_DEPTH[Determine target node depth]

    GET_DEPTH --> DEPTH0{Depth 0 - Root?}
    DEPTH0 -->|Yes| ROOT_CONTEXT[Read project vision]
    ROOT_CONTEXT --> GEN_FEATURES[Generate major feature concepts]

    DEPTH0 -->|No| DEPTH1{Depth 1 - Feature?}
    DEPTH1 -->|Yes| FEATURE_CONTEXT[Read feature description]
    FEATURE_CONTEXT --> GEN_CAPABILITIES[Generate capability concepts]

    DEPTH1 -->|No| DETAIL_CONTEXT[Read parent capability]
    DETAIL_CONTEXT --> GEN_DETAILS[Generate implementation concepts]

    GEN_FEATURES --> SIBLINGS
    GEN_CAPABILITIES --> SIBLINGS
    GEN_DETAILS --> SIBLINGS

    SIBLINGS[Review existing sibling nodes] --> GIT_CONTEXT[Analyze relevant git commits]
    GIT_CONTEXT --> CREATE[Create 1-3 new story concepts]

    CREATE --> LIMIT{Exceeded 3 stories?}
    LIMIT -->|Yes| TRIM[Trim to maximum 3]
    LIMIT -->|No| FORMAT
    TRIM --> FORMAT

    FORMAT[Format as user stories] --> QUALITY{Pass quality checks?}

    QUALITY -->|No| REVISE[Revise story content]
    REVISE --> QUALITY

    QUALITY -->|Yes| OUTPUT([Return generated stories])

    style OUTPUT fill:#90EE90
```

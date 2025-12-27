# Three-Field Workflow Model

Visual representations of the stage, hold, and disposition states used by the story-tree system.

---

## Definitions

| Term | Definition |
|------|------------|
| **Story node** | A unit of work in the hierarchical backlog—can be an epic, feature, capability, or task depending on depth. May have its own direct work AND children simultaneously. |

---
Stories progress through stages, with holds and dispositions as orthogonal states:


| Stage | Definition |
|-------|------------|
| **concept** | New idea proposed |
| **planning** | Implementation being planned; dependencies being verified |
| **executing** | Own code in progress; children's code in progress |
| **reviewing** | Own code under review; reviewing child code |
| **verifying** | Own implementation being tested; verifying integration with children |
| **implemented** | Own code complete; all children implemented and integrated |
| **ready** | Own work fully tested; entire subtree fully tested |
| **released** | Shipped |

---



| Hold States | Definition |
|------|------------|
| *(no hold)* | Story is not blocked and can progress |
| **🔥 broken** | Implementation has issues |
| **⚔ conflicted** | Scope overlaps another story |
| **🚧 blocked** | External dependency missing (not a choice to stop) |
| **⏳ escalated** | Requires human decision |
| **⏸ paused** | Intentionally stopped (not blocked by external factors) |
| **💎 polish** | Minor refinements before progressing |
| **📋 queued** | Processing delayed pending completion of prerequisite steps |
| **💭 wishlisted** | Low priority, indefinite deferral |

---

| Dispositions | Definition |
|-------------|------------|
| *(not disposed)* | Story remains active in the tree |
| **🚫 infeasible** | Cannot be built |
| **❌ rejected** | Explicitly declined |
| **👯 duplicative** | Duplicate of another story |
| **⚠️ deprecated** | No longer recommended |
| **🛑 legacy** | Outdated or superseded |
| **📦 archived** | Stored away for reference |

---

## Stage Transitions

```mermaid
flowchart LR
    concept[concept]
    planning[planning]
    executing[executing]
    reviewing[reviewing]
    verifying[verifying]
    implemented[implemented]
    ready[ready]
    released[released]

    concept -->|approved| planning
    planning -->|auto-queue| executing
    executing -->|auto-queue| reviewing
    reviewing -->|auto-queue| verifying
    verifying -->|auto-queue| implemented
    implemented -->|auto-queue| ready
    ready -->|auto-queue| released

    classDef conceptBox fill:#66CC00,stroke:#52A300,color:#fff
    classDef planningBox fill:#00CC66,stroke:#00A352,color:#fff
    classDef executingBox fill:#00CCCC,stroke:#00A3A3,color:#fff
    classDef reviewingBox fill:#0099CC,stroke:#007AA3,color:#fff
    classDef verifyingBox fill:#0066CC,stroke:#0052A3,color:#fff
    classDef implementedBox fill:#0033CC,stroke:#0029A3,color:#fff
    classDef readyBox fill:#0000CC,stroke:#0000A3,color:#fff
    classDef releasedBox fill:#3300CC,stroke:#2900A3,color:#fff
    class concept conceptBox
    class planning planningBox
    class executing executingBox
    class reviewing reviewingBox
    class verifying verifyingBox
    class implemented implementedBox
    class ready readyBox
    class released releasedBox
```

---

## Detailed Stage Workflows

For detailed diagrams of each stage's internal workflow:

| Stage | Details |
|-------|---------|
| concept | @workflow1-concept.md |
| planning | @workflow2-planning.md |
| executing | @workflow3-executing.md |
| reviewing | @workflow4-reviewing.md |
| verifying | @workflow5-verifying.md |
| implemented | @workflow6-implemented.md |
| ready | @workflow7-ready.md |

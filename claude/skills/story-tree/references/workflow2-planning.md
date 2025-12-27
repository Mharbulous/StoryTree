# Planning Stage

> For definitions of stages, holds, and dispositions, see @workflow-three-field-model.md

---

## Stage Diagram

```mermaid
flowchart TB
    concept[concept: approved] -->|approved| p_q

    subgraph planning_stage [planning]
        p_q[queued]
        p_clear[no hold]
        p_q --> p_clear
    end

    p_clear -->|auto-queue| executing[executing: queued]

    classDef conceptBox fill:#66CC00,stroke:#52A300,color:#fff
    classDef planningBox fill:#00CC66,stroke:#00A352,color:#fff
    classDef executingBox fill:#00CCCC,stroke:#00A3A3,color:#fff
    class concept conceptBox
    class planning_stage planningBox
    class executing executingBox
```

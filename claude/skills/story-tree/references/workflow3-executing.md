# Executing Stage

> For definitions of stages, holds, and dispositions, see @workflow-three-field-model.md

---

## Stage Diagram

```mermaid
flowchart TB
    planning[planning: no hold] -->|auto-queue| e_q

    subgraph executing_stage [executing]
        e_q[queued]
        e_h[holds]
        e_clear[no hold]
        e_q --> e_h
        e_h --> e_clear
        e_q --> e_clear
    end

    e_clear -->|auto-queue| reviewing[reviewing: no hold]

    classDef planningBox fill:#00CC66,stroke:#00A352,color:#fff
    classDef executingBox fill:#00CCCC,stroke:#00A3A3,color:#fff
    classDef reviewingBox fill:#0099CC,stroke:#007AA3,color:#fff
    class planning planningBox
    class executing_stage executingBox
    class reviewing reviewingBox
```

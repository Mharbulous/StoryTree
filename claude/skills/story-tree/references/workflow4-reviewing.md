# Reviewing Stage

> For definitions of stages, holds, and dispositions, see @workflow-three-field-model.md

---

## Stage Diagram

```mermaid
flowchart TB
    executing[executing: no hold] -->|auto-queue| r_q

    subgraph review_stage [reviewing]
        r_q[queued]
        r_h[holds]
        r_clear[no hold]
        r_q --> r_h
        r_h --> r_clear
        r_q --> r_clear
    end

    r_clear -->|auto-queue| verifying[verifying: no hold]

    classDef executingBox fill:#00CCCC,stroke:#00A3A3,color:#fff
    classDef reviewingBox fill:#0099CC,stroke:#007AA3,color:#fff
    classDef verifyingBox fill:#0066CC,stroke:#0052A3,color:#fff
    class executing executingBox
    class review_stage reviewingBox
    class verifying verifyingBox
```

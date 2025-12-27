# Implemented Stage

> For definitions of stages, holds, and dispositions, see @workflow-three-field-model.md

---

## Stage Diagram

```mermaid
flowchart TB
    verifying[verifying: no hold] -->|auto-queue| i_q

    subgraph impl_stage [implemented]
        i_q[queued]
        i_h[holds]
        i_clear[no hold]
        i_q --> i_h
        i_h --> i_clear
        i_q --> i_clear
    end

    i_clear -->|auto-queue| ready[ready: queued]

    classDef verifyingBox fill:#0066CC,stroke:#0052A3,color:#fff
    classDef implementedBox fill:#0033CC,stroke:#0029A3,color:#fff
    classDef readyBox fill:#0000CC,stroke:#0000A3,color:#fff
    class verifying verifyingBox
    class impl_stage implementedBox
    class ready readyBox
```

# Verifying Stage

> For definitions of stages, holds, and dispositions, see @workflow-three-field-model.md

---

## Stage Diagram

```mermaid
flowchart TB
    reviewing[reviewing: no hold] -->|auto-queue| v_q

    subgraph verify_stage [verifying]
        v_q[queued]
        v_h[holds]
        v_clear[no hold]
        v_q --> v_h
        v_h --> v_clear
        v_q --> v_clear
    end

    v_clear -->|auto-queue| implemented[implemented: queued]

    classDef reviewingBox fill:#0099CC,stroke:#007AA3,color:#fff
    classDef verifyingBox fill:#0066CC,stroke:#0052A3,color:#fff
    classDef implementedBox fill:#0033CC,stroke:#0029A3,color:#fff
    class reviewing reviewingBox
    class verify_stage verifyingBox
    class implemented implementedBox
```

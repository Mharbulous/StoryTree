# Concept Stage

> For definitions of stages, holds, and dispositions, see @workflow-three-field-model.md

---

## Stage Diagram

```mermaid
flowchart TB
    subgraph concept_stage [concept]
        c_clear[no hold]
        c_ai((🤖 vet concept))
        c_refine((AI refines))
        c_conf[conflicted]
        c_dup[duplicative]
        c_del([deleted])
        c_e[escalated]
        c_human((Human review))
        c_paused[paused]
        c_polish[polish]
        c_wish[wishlisted]
        c_hold((on hold))
        c_rej[rejected]
        c_disposed([disposed])

        c_refine --> c_clear
        c_clear --> c_ai
        c_ai --> c_conf --> c_del
        c_ai --> c_dup --> c_del
        c_ai --> c_e --> c_human
        c_human --> c_paused --> c_hold
        c_human --> c_polish --> c_refine
        c_human --> c_wish --> c_hold
        c_human --> c_rej --> c_disposed
    end

    c_human -->|approved| planning[planning: no hold]

    classDef conceptBox fill:#66CC00,stroke:#52A300,color:#fff
    classDef planningBox fill:#00CC66,stroke:#00A352,color:#fff
    class concept_stage conceptBox
    class planning planningBox
```

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
| **📋 queued** | Awaiting automated processing |
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

Holds gate progression within each stage. Clearing all holds triggers automatic transition to the next stage's queue.

```mermaid
flowchart TB
    subgraph concept_stage [concept]
        c_refine((🤖 AI refines))
        c_clear[no hold]
        c_ai((🤖 AI review))
        c_conf[⚔ conflicted]
        c_dup[👯 duplicative]
        c_del([deleted])
        c_e[⏳ escalated]
        c_human((👤 Human review))
        c_paused[⏸ paused]
        c_polish[💎 polish]
        c_wish[💭 wishlisted]
        c_hold[on hold]
        c_rej[❌ rejected]
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
        c_human -->|approved| p_q
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

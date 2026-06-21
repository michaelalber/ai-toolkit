# PARA Classification Heuristics

The authoritative source is Tiago Forte's PARA method (fortelabs.com/blog/para). PARA is a
personal-knowledge-management methodology, not an engineering standard — these heuristics encode
canonical PARA practice and are not drawn from the grounded-code-mcp collections.

## The Four Categories — distinguishing criteria

| Category | Definition | Litmus test | Has an end? |
|----------|-----------|-------------|-------------|
| **Project** | A short-term effort with a specific goal and a finish line. | "Am I working toward a concrete outcome with a deadline (explicit or implied)?" | Yes — it completes. |
| **Area** | An ongoing responsibility with a standard to maintain over time. | "Is there a standard here I must uphold indefinitely, with no finish line?" | No — it continues. |
| **Resource** | A topic of ongoing interest or reference material, not tied to a current goal. | "Is this something I'm curious about / may reference later, but am not actively delivering on?" | No — but inactive. |
| **Archive** | An inactive item from any of the above. | "Is this from a completed project, a dropped area, or a resource I no longer follow?" | n/a — cold storage. |

**Project vs. Area** is the most common confusion. *Run a marathon in May* is a Project (goal + end).
*Health* is an Area (a standard maintained forever). Projects usually live **inside** the Area they
serve, but are filed under Projects because they are more actionable.

**Area vs. Resource** turns on responsibility. An Area is something you are *accountable* for
maintaining (Finances, a product you own). A Resource is something you are merely *interested in*
(a topic, a technique, a reference collection).

## Actionability decision tree

Evaluate top to bottom. **File at the first match** — the most actionable home wins.

```
1. Is this needed to move a specific, goal-bearing effort forward right now?
   → PROJECT.  Place under Projects/<project-name>/.

2. Does it support a standard you are responsible for maintaining over time
   (no end date), but isn't tied to one active goal?
   → AREA.  Place under Areas/<area-name>/.

3. Is it reference material / a topic of interest you may want later, with no
   current responsibility or goal attached?
   → RESOURCE.  Place under Resources/<topic>/.

4. Is it from a finished project, a responsibility you no longer hold, or a topic
   you no longer follow?
   → ARCHIVE.  Place under Archive/<original-category>/<name>/.
```

### Tie-breakers
- **Project vs Area:** if a deadline or concrete deliverable exists, choose Project.
- **Area vs Resource:** if you are accountable for it, choose Area; if merely interested, Resource.
- **Anything vs Archive:** only Archive when there is no active project, area, or living interest it serves.
- When genuinely split between two *active* categories, pick the more actionable and note the
  alternative in the rationale — `para-review` will catch it if wrong. Do not stall on a perfect call.

## Edge cases

| Situation | Resolution |
|-----------|-----------|
| Item serves several projects | File under the *most active* project; reference (link/shortcut) from the others — don't duplicate the content. |
| A Resource suddenly becomes goal-driven | Promote it: move into Projects under the new goal. PARA expects category movement. |
| A completed Project's outputs are still useful reference | Archive the project; if a discrete asset has lasting reference value, copy that asset into Resources. |
| Pure inbox dump with no clear home | Leave in the inbox, tag it, and let `para-review`'s ritual process it — do not force a wrong category. |
| Sensitive / PII document | File, but never write its contents into the index summary; record only a neutral title. |

## Anti-patterns (do not do these)

- **Filing by topic, not actionability.** A "Marketing" mega-folder spanning P/A/R defeats PARA.
- **Inventing a fifth top-level bucket** ("Someday", "Misc") — use the inbox + Archive instead.
- **Deep taxonomies up front.** Start flat; let structure emerge inside P/A/R as it's needed.
- **Refusing to file because the category is uncertain.** Place it; movement is cheap, paralysis is not.
- **Duplicating content across categories.** One authoritative copy; link from the rest.

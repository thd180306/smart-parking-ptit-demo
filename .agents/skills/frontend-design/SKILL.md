---
name: frontend-design
description: "Professional UI/UX design and frontend engineering skill. Combines Impeccable's craft floor, 8-state interactive discipline, and audit rigour with Hallmark's macrostructure variety, anti-AI-slop gates, and distinct visual fingerprints. Use for creating, redesigning, auditing, or polishing web interfaces, dashboards, control consoles, mobile web apps, components, and forms."
user-invocable: true
version: 1.0.0
---

# Frontend Design Skill

This skill operationalizes a rigorous, production-grade frontend design intelligence system. It ensures every UI generated or modified has a clear authorial point of view, strict token discipline, responsive resilience, and complete immunity to generic AI-template clichés.

---

## 1. The 10-Phase Design Flow

Every significant UI task must proceed through these structured stages:

```
[1. RESEARCH] ─────────────► [2. USER GOAL] ──────────► [3. INFORMATION HIERARCHY]
                                                                │
[6. IMPLEMENTATION] ◄─────── [5. DESIGN SYSTEM] ◄────── [4. MACROSTRUCTURE]
       │
       ▼
[7. BROWSER VERIFY] ───────► [8. SELF-CRITIQUE] ──────► [9. SLOP AUDIT] ───► [10. POLISH]
```

### Phase 1: Research & Pre-flight Inspection
* Inspect existing templates, CSS files, tokens, and font declarations in the codebase.
* Read `DESIGN.md` for locked project tokens, color semantics, and layout guidelines.
* Verify existing routes, state models, and backend endpoints.

### Phase 2: Understand User Goal & Surface Register
Identify which register the surface belongs to:
* **`Operate`** (Admin Console, Data Tables, Barrier Simulator): Prioritize scanning speed, keyboard accessibility, high contrast, low visual noise, and clear error recovery.
* **`Persuade`** (Login, Landing): Focused composition, clear value proposition, frictionless input flow.
* **`Experience`** (Mobile Wallet): Touch ergonomics (≥ 44px tap targets), bold balance readouts, immediate feedback.

### Phase 3: Information Hierarchy
* Establish what is **Primary** (the single core action, e.g., Quét thẻ / Mở cổng), **Secondary** (supporting metrics & table history), and **Tertiary** (metadata, timestamps, colophon).
* Ensure visual weight directly reflects informational priority.

### Phase 4: Macrostructure & Visual Fingerprint
* Select an intentional macrostructure (e.g., *Workbench*, *Bento Grid*, *Data Table Index*, *Split Studio*).
* **Reject the AI default:** Avoid the standard "Hero + 3 identical cards + CTA" template.
* Establish clear asymmetrical spacing (more space above headings than below).

### Phase 5: Design System & Token Binding
* Lock color tokens: `--primary`, `--secondary`, `--accent`, `--success`, `--danger`, `--warning`.
* Lock typography: Primary body font paired with tabular numerals for figures (`tabular-nums`).
* All colors, fonts, and spacing must reference variables defined in `DESIGN.md`.

### Phase 6: Production Implementation
* Write clean, semantic HTML5 (`<main>`, `<nav>`, `<header>`, `<section>`, `<table>`, `<figure>`).
* Ensure all interactive elements include code for **8 states**: `default`, `hover`, `:focus-visible`, `:active`, `disabled`, `loading`, `error`, `success`.
* Enforce single-line clickable affordances (`white-space: nowrap;`).

### Phase 7: Browser & Responsive Verification
* Check responsive behavior at: `320px`, `375px`, `414px`, `768px`, `1280px`, `1920px`.
* Enforce `overflow-x: clip;` on `html, body` to eliminate horizontal scrollbars without breaking sticky elements.
* Check image and grid tracks with `minmax(0, 1fr)` to prevent layout blowout.

### Phase 8: Pre-Emit Self-Critique (Six Axes)
Score the design 1–5 on each axis before presenting:
* **P — Philosophy:** Does this screen have a distinct and defensible purpose?
* **H — Hierarchy:** Is the most important element immediately obvious?
* **E — Execution:** Are paddings, borders, shadows, and alignment mathematically consistent?
* **S — Specificity:** Does this feel authentically designed for PTIT Parking?
* **R — Restraint:** Have unnecessary decorations, gradients, and redundant cards been cut?
* **V — Variety:** Is this visually and structurally distinct from generic boilerplate?
*(Any score < 3 requires an immediate revision pass).*

### Phase 9: Anti-AI-Slop Audit (The 12 Gates)
Verify zero violations against the 12 Slop Gates:
1. ❌ No purple-to-blue gradient backgrounds.
2. ❌ No gradient text fills (`background-clip: text`).
3. ❌ No Inter used without distinct pairings or tabular numerals.
4. ❌ No symmetrical 3-card identical feature grids.
5. ❌ No nested cards (card inside a card).
6. ❌ No colored side-stripe borders (`border-left: 4px solid ...`).
7. ❌ No fabricated data or placeholder testimonials.
8. ❌ No two-line wrapping button labels on mobile.
9. ❌ No mixed icon sets or raw emojis as primary feature icons.
10. ❌ No italic headings or italic emphasis words in upright headlines.
11. ❌ No fake OS/browser chrome redrawn in HTML.
12. ❌ No pure `#000` or `#fff` without subtle anchor-hue tinting.

### Phase 10: Final Polish Pass
* Verify hover transitions (`150ms ease`), focus rings (`2px solid` with offset), and tabular alignments.
* Test empty states, loading states, and error alerts.

---

## 2. Quick Command Verbs for Agents

| Command | Purpose |
| :--- | :--- |
| `frontend-design shape <feature>` | Plan IA, information hierarchy, and macrostructure before writing code. |
| `frontend-design audit <target>` | Check a template or CSS file against the 12 Anti-Slop Gates and WCAG contrast. |
| `frontend-design critique <target>` | Perform 6-axis heuristic review (P, H, E, S, R, V). |
| `frontend-design polish <target>` | Final alignment pass: spacing, tabular nums, focus rings, state completeness. |
| `frontend-design distill <target>` | Strip visual clutter, remove redundant card wrappers, increase breathing room. |

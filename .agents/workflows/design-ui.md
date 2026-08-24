# Workflow: Design & Implement Frontend UI

This workflow guides an AI coding agent step-by-step through designing, building, or refactoring a UI component or page.

---

## Step 1: Pre-Flight Check
1. Open and review `DESIGN.md`.
2. Inspect the target template in `Templates/` and stylesheets in `Static/css/`.
3. Confirm existing token names and color variables.

## Step 2: Define Hierarchy & Macrostructure
1. Name the primary user action on this screen.
2. Select a structural layout pattern (e.g., Workbench, Asymmetric Grid, Data Colophon).
3. Confirm that the structure does NOT replicate the generic "Hero + 3 equal cards" AI pattern.

## Step 3: Implement Semantic Markup & Tokens
1. Write clean semantic HTML5.
2. Reference design tokens from `DESIGN.md` via CSS custom properties (`var(--primary)`, `var(--accent)`, etc.).
3. Ensure numeric and currency columns use `font-variant-numeric: tabular-nums;`.

## Step 4: Implement 8-State Interactive Discipline
Ensure every button, form input, and interactive row implements:
- Default
- Hover (`background-color` or brightness shift)
- Focus-visible (`2px outline var(--focus-ring)` with `2px offset`)
- Active (`transform: translateY(1px)`)
- Disabled (`opacity: 0.55; cursor: not-allowed;`)
- Loading / Pending
- Error (border + descriptive text)
- Success (confirm feedback)

## Step 5: Responsive & Anti-Slop Verification
1. Verify layout resilience across mobile widths (`320px`, `375px`, `414px`, `768px`, `1280px`).
2. Verify that no button or CTA label wraps onto two lines (`white-space: nowrap;`).
3. Check `html, body` has `overflow-x: clip;`.
4. Ensure contrast meets WCAG 2.1 AA (≥ 4.5:1 for body text, ≥ 3.0:1 for large headers).

## Step 6: Self-Critique & Polish
1. Score the UI on the 6 axes: Philosophy, Hierarchy, Execution, Specificity, Restraint, Variety.
2. Polish any uneven margins, misaligned table cells, or missing focus states.
3. Save and run automated test suites (`test_system.py`, `test_sessions.py`) to guarantee zero regression.

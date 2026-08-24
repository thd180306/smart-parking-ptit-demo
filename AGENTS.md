# AGENTS.md — Directives for AI Coding Agents & Pair Programmers

Welcome to the **PTIT Smart Parking Management System** codebase.  
As an AI coding agent, you are responsible for maintaining exceptional code quality, architectural consistency, and award-winning frontend design.

---

## 1. Master Design System Rule
**`DESIGN.md` is the absolute source of truth for all visual and UX decisions in this repository.**  
Before writing or modifying any HTML, CSS, JavaScript, or UI templates:
1. **Read `DESIGN.md`** at the project root.
2. Follow its token definitions, type scales, spacing multiples, 8-state interactive rules, and anti-AI-slop prohibitions.
3. Never improvise ad-hoc inline colors or unvetted UI patterns.

---

## 2. Mandatory Skill Usage
When asked to create, redesign, critique, or significantly update any frontend interface in this project, you must invoke and follow the **`frontend-design`** skill located at:  
`.agents/skills/frontend-design/SKILL.md`

Follow the 10-phase repeatable engineering workflow:
```
RESEARCH 
  → UNDERSTAND USER GOAL 
  → INFORMATION HIERARCHY 
  → MACROSTRUCTURE 
  → VISUAL DIRECTION 
  → DESIGN SYSTEM TOKENS 
  → IMPLEMENTATION 
  → BROWSER / TEST VERIFICATION 
  → SELF-CRITIQUE 
  → AUDIT & POLISH
```

---

## 3. Core Engineering & Safety Principles

### 3.1 Preserve Existing Architecture & Functionality
* This project runs on **Python Flask + SQLite + Vanilla JS/CSS**.
* **Do not replace the framework** or introduce heavyweight JS libraries (React, Vue, Tailwind) unless explicitly commanded by the user.
* Preserve existing backend API contracts (`/transaction`, `/force_action`, `/api/staff_income`, `/stats`, etc.).
* Session isolation between Admin (`session['admin_user']`) and Student (`session['student_user']`) must never be broken.

### 3.2 Component & Token Reuse
* Check `Static/css/admin_style.css` and `Static/css/user_style.css` before writing new CSS rules.
* Reuse existing CSS custom properties defined in `DESIGN.md`.
* Avoid duplicate modal or button styles.

### 3.3 Anti-Slop Enforcement
* No purple/blue gradient backgrounds.
* No gradient text headlines.
* No two-line wrapping buttons on mobile viewports (320px–414px).
* No unmotivated emojis as primary icons.
* Always enforce `font-variant-numeric: tabular-nums;` for monetary and time data.

### 3.4 Verification Before Completion
* Execute tests (e.g. `test_system.py`, `test_sessions.py`) to verify that changes did not break session handling, database transactions, or responsive layouts.

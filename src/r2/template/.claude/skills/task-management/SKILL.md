---
name: task-management
description: >
  Manages the revision dashboard (paper/revision/todo.md): adds tasks from reviews,
  sessions, or user requests; marks items done with results; evaluates progress;
  updates the progress bar and lane counts. Single source of truth for what
  needs doing and what has been done. Trigger on: "add task," "mark done,"
  "what's left," "todo status," "update todos," "action items," "what should
  I work on next," "prioritize," or any mention of paper/revision/todo.md. Also
  trigger proactively: (1) after a review skill run, (2) at session end when
  substantive work was discussed, (3) after completing any analysis or writing
  task that corresponds to an open item.
---

# Task Management

## Purpose

`paper/revision/todo.md` is the single persistent file tracking all revision work.
This skill governs every read and write to that file: adding items, marking
them done, updating progress, and evaluating what remains.

## File Location and Format

```
paper/revision/
├── review/    ← full review reports
├── todo.md    ← active items (the working queue)
└── done.md    ← completed items with concern/resolution records
```

The dashboard uses this structure:

```markdown
# Revision Dashboard

**Progress**
`[################----] N/M complete (X%)`

| Lane | Count | Snapshot |
| --- | ---: | --- |
| Critical | ... | ... |
| Important | ... | ... |
| Minor | ... | ... |
| Done | ... | Archived below |

[Category links]

---

## Category (e.g., Identification, Robustness, Measurement, Framing, Citation)

### NN. Task title
`PRIORITY` · `EFFORT`

Description. **Deliverable in bold.** → target file/section

---

## Done

**N completed**

### Category

| # | Task | Result |
| ---: | :----- | :------- |
| NN | Task name (date) | Brief result |
```

## Operations

### ADD — New tasks

Sources: reviews, sessions, user requests, or proactive identification.

1. **Read** `paper/revision/todo.md` first. Never add duplicates.
2. **Assign**: sequential ID (next available number), priority (`CRITICAL` /
   `IMPORTANT` / `MINOR`), effort (`EASY` / `MODERATE` / `HARD`), category
   (Identification / Robustness / Measurement / Framing / Citation / other).
3. **Write** the item under its category section using the format above.
4. **Update** the progress bar, lane counts, and total.

Priority rules:
- `CRITICAL`: Would cause desk reject or fatal R&R. Severity "Serious" +
  threat type "Identification Failure" or "Non-Novelty."
- `IMPORTANT`: Strengthens the paper materially. Severity "Serious" + other threats.
- `MINOR`: Nice to have. Severity "Minor" or polish items.

From reviews specifically:
- Extract the constructive suggestion (the actionable part)
- Deduplicate: if multiple reviewers flag the same issue, one item with all refs
- Order within tiers by effort (easy first)

### DONE — Mark items complete

**Gatekeeper principle.** Before marking any item "done" or "not needed," go
back to the original reviewer concern in `paper/revision/review/` and verify the
resolution actually addresses it. The user may dismiss an item as unnecessary,
but if the reviewer's point has genuine merit, **push back**. Specifically:

- Re-read the reviewer's objection, threat type, and severity.
- Check whether the current manuscript/analysis actually resolves it.
- If the user says "not needed" but the reviewer's concern is valid and
  unaddressed, say so directly: "The reviewer's point stands because [X].
  Dismissing it risks [Y] at review."
- Only mark "not needed" when you can articulate why the concern does not
  apply — not just because the user said so.

This is not about being difficult. It is about protecting the paper from a
real reviewer who will raise the same objection. Better to fight about it now
than get desk-rejected later.

When a task is genuinely completed:

1. **Remove** the item from `todo.md`.
2. **Add** a full entry to `done.md` under the appropriate category subsection.
3. **Include result**: brief description of what was found/done. For analysis
   tasks, include key numbers (coefficient, p-value). For fragile/null results,
   say so honestly.
4. **Include date** in YYYY-MM-DD format in the Date column.
5. **Update** progress bar, lane counts, total.

Done section ordering:
- **Primary sort: category** — group under category subsections (Identification,
  Robustness, Measurement, Framing, Citation).
- **Secondary sort: date** — within each category, newest entries at the bottom
  so the table reads chronologically top-to-bottom.

Result categories for Done entries:
- **Passed**: robustness check confirms the result holds
- **Fragile**: check reveals weakness — note how the paper should handle it
- **Already addressed**: manuscript already covers the concern (cite the line)
- **Not needed**: reviewer's concern does not apply (state why explicitly)
- **Superseded**: addressed by a different item

### EVALUATE — Assess progress

When asked "what's left," "status," or "what should I work on":

1. Read `paper/revision/todo.md`.
2. List open items by priority, then effort.
3. Flag stale items (7+ days old, not started).
4. Recommend next action based on priority and dependencies.

### EDIT — Modify existing items

When priorities change, items need re-scoping, or new information emerges:

1. Update the item in place (description, priority, effort).
2. If re-prioritizing, move between category sections if needed.
3. Update lane counts.

## Integration

- **review**: After every review, extract all issues into the dashboard.
- **verification**: Before reporting "done," check if work corresponds to an
  open item and mark it complete.
- **analysis/writing**: When executing a change, reference the todo ID.
- **session end**: Scan conversation for discussed-but-unfinished work and add.

## Rules

- Never delete an unchecked item without moving it to Done (even if skipped —
  record the reason).
- Progress bar must always match the actual count of open vs done items.
- Every Done entry needs a result — "done" alone is insufficient.
- Keep the dashboard scannable: one-line descriptions in tables, detail in
  the active section only.
- Respect the user's formatting preferences (no emojis, category sections,
  `PRIORITY` · `EFFORT` tags, bold deliverables).

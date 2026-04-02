# CLAUDE.md — POLYPRO Working Constitution

This file is the permanent operating contract for all Claude sessions in this project.
It is not a roadmap, backlog, or vision document. It is a binding ruleset.

---

## 1. Role and Authority

- Claude is the **implementer**. Nothing more.
- Product architecture, scope, feature order, versioning, and release authority belong to the user.
- Claude does not propose features unless asked.
- Claude does not make product decisions.
- Claude does not override user judgment with its own.

---

## 2. Non-Negotiable Rules

- No feature is added without explicit user approval.
- No scope expansion, even if technically trivial.
- No silent behavior changes via fallback logic.
- No config and runtime state mixed together.
- No admin/user boundary left ambiguous.
- No duplicated truth sources created.
- No hidden coupling between components.
- No global user settings modified without approval.

---

## 3. Scope Discipline

- Every task begins with: *"In this task I am doing X. I am not doing Y."*
- If a task contains multiple features, Claude asks the user to confirm the sequence before starting.
- Refactoring is not done unless explicitly requested.
- "It would be nice to have" is not a valid reason to expand scope.
- Abstractions are only introduced when the current task requires them.

---

## 4. Architecture Discipline

- Backend is the single source of truth for business logic and data.
- Frontend does not produce trading truth, pricing truth, or business state.
- Frontend is never a second data source.
- Hidden coupling between layers is not introduced.
- Duplicated truth sources are not created.
- Silent fallback must not change observable behavior.
- Config values and runtime state are always kept separate.
- Admin/user permission boundaries are explicit and documented before implementation.

---

## 5. Testing Discipline

- Untested work is not considered done.
- Tests are written for every changed or added unit of behavior.
- Test results (pass/fail counts, failing test names) are reported in every delivery.
- Flaky tests are flagged explicitly — they do not count as passing.
- Test framework and coverage targets are set by the user, not assumed.

---

## 6. Reporting Discipline

Every delivery includes:

```
DELIVERY REPORT
───────────────
Task: [task name]
Changed files:
  - [path] — [what changed]
Test results:
  - [test name]: PASS / FAIL
Commit: [hash] [message]
Push: OK / FAIL / pending
Risks:
  - [explicit, or "None"]
```

No delivery is considered complete without this report.

---

## 7. Git Discipline

- Commit message format: `[type]: [short description]`
  - Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`
- Each commit contains one logical change.
- Sensitive files (`.env`, credentials) are never committed.
- `.gitignore` is verified before every commit.
- Force push is never done without explicit user instruction.
- Push result is always reported separately.

---

## 8. Recommendation vs Implementation

- A recommendation is clearly labeled as such: *"Suggestion: ..."*
- A recommendation is never acted upon without user approval.
- Claude does not blur the line between "I suggest X" and "I did X."
- If the user has not approved it, it has not been implemented.

---

## 9. Version-by-Version Delivery

- All progress is made in small, verifiable steps.
- No version skipping.
- Each version is functional and testable on its own.
- Version scope is defined by the user, not expanded by Claude.
- Version boundaries are respected even when "one more thing" seems easy.

---

## 10. Workspace and Legacy Code Rule

- The current workspace is a clean slate. No legacy is assumed.
- No old project, old repo, old bot, or old architecture is referenced.
- No existing workspace content is treated as inherited context.
- If the user explicitly references prior work, Claude uses only what the user provides — not inferred from git history or workspace files.

---

## 11. Definition of Done

A task is done **only when all of the following are true**:

- [ ] Implementation matches the approved task description exactly
- [ ] Tests are written and passing
- [ ] Changed files are listed in the delivery report
- [ ] Risks are documented
- [ ] Changes are committed with a valid message
- [ ] Push status is confirmed
- [ ] CHANGELOG.md is updated

Partial completion is not completion.

---

## 13. Permission and Operating Mode

- Claude operates in **bypassPermissions** mode at all times in this project.
- Claude never prompts the user with allow / allow once / deny dialogs.
- This is enforced via `.claude/settings.local.json` (`defaultMode: bypassPermissions`).
- If a permission prompt appears, it means settings were reset — restore `defaultMode: bypassPermissions` in `.claude/settings.local.json` immediately.

---

## 12. Output Format Expectations

- Responses are concise and direct.
- Delivery reports follow the format in Section 6.
- Suggestions are labeled separately from actions.
- No trailing summaries that restate what was just done.
- No speculative commentary about future features.
- No padding, filler, or hedging language.

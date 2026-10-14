# Independent Windows Python3.12 replay of PR1298

All23 existing research tests pass on Windows CPython3.12.7 with zero skips,
including the registered-package success and exit7 mutation test that PR1298's
reported Python3.14 run skipped. Two source-reversion controls also fail as
expected. This closes that specific environment-evidence gap; it does not add
another portability fix or a mathematical result.

## Scope and reproduction

Audited PR1298 head: `e76026571dbfa7299bf474b941c9abeb5bd556b3`.
Base main: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The audit verifies SHA256 and Git-blob pins for33 base fixture inputs and six
exact overlaid PR files, then executes them in a disposable workspace fixture.
The calling checkout is never edited. UTF8 mode is explicitly disabled and
the child pipes use cp1252. Frozen scientific sources remain unchanged.

On Windows with Python3.12, from the repository root:

```text
python -B research/pr1298-python312-audit/verify.py
```

Expected: `PASS_PR1298_WINDOWS_PY312_AUDIT`,23 tests,0 skips,2 controls.
The overlap-only source reversion must raise UnicodeEncodeError; the metadata
source reversion must raise UnicodeDecodeError. Neither control executes the
old process-timeout bug or intentionally leaks a process. VALIDATION.json
retains the observed environment and complete test output.

This is independent execution of the predecessor suite, not an independently
implemented checker. No Linux/macOS, native supplier, cold mathematical replay,
or kappa claim. The predecessor's taskkill-on-PATH assumption remains.
This Windows-only handoff is not registered for the generic Linux CI hook;
WINDOWS-VERIFY.json records the explicit manual command and input closure.

## Open next questions

Run this exact patch on Linux/macOS using its original suite. Cross-platform
patches need evidence from those hosts; the blocker here is host availability.
Structured scope and next questions are in TASK.json.

## Credit

Portability fixes and regression tests: PR1298's author, retained byte-for-byte.
Original onboarding scripts: Douglas Colkitt with the credited OpenAI Codex
assistance. Independent execution prepared for woklerx with substantial OpenAI
Codex assistance. Apache-2.0; repository LICENSE applies. No independent human
review is claimed. No new PR recommended: send this focused evidence to PR1298.

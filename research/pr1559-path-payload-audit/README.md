# Reproduce and repair spaced-path failure in PR1559 payload comparison adapter

Intentional independent audit of [PR1559](https://github.com/CrocSwap/integer-mult-bounds/pull/1559), exact head `c4f8af1dcf9fc2317c893b6b250007ded5ef879f`. This is a corroborating review/handoff, not a new supplier or selected-frontier change.

The pinned adapter leaves comparison operands unquoted. Git Bash on the actual spaced checkout causes 8 focused representation failures. The bounded reproducer confirms both adapted sites reject spaced paths; the supplied quote patch passes both. Independent CLI fixtures accept 24 equivalent payload cases and reject 20 changed/corrupt cases under normal and optimized Python.

## Reproduction

Start from main checkpoint `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The independent checker imports no predecessor executable except intentionally executing the exact pinned adapter under test; it reads only declared exact Git objects. Fetch the reviewed head before replay:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git c4f8af1dcf9fc2317c893b6b250007ded5ef879f
python -I -O -B research/pr1559-path-payload-audit/verify.py
```

The shell-site check also requires Bash; on Windows set AUDIT_BASH to installed Git Bash. UPSTREAM-FIX.patch targets pending PR1559. PATH-FAILURE.txt retains the actual rejection.

SOURCES.json binds every consumed source by exact Git blob and SHA256. RESULT.json is recomputed, not trusted as the answer. TASK.json preserves the original random allocation and refined scope. The prior author registered replay was run separately and failed 8 focused representation tests on the spaced checkout; 4 other groups passed. The independent audit corroborates the path defect and the bounded repair. Delivered logs retain the upstream failures and name the environment.

## Scope

Only two adapted comparison sites are repaired. The inherited full native shell pipeline has other path assumptions and was not run or claimed Windows portable. No frozen source is edited. UPSTREAM-FIX.patch targets pending PR1559, not main.

## Open next questions

Apply the small patch to PR1559 and expand its test to quote operand paths explicitly; then decide whether the rest of the shell pipeline should promise paths with spaces.

## Credit

Hanson Sun PR1559; DreamingOfClouds PR589/545, eumemic PR555/493; Maxime Fleury/Antoine Olivier gzip-payload convention. Prepared by woklerx with substantial OpenAI Codex assistance. The checker is implementation-independent where stated, not independent human or proof-kernel review. New audit material is Apache-2.0; upstream source notices remain unchanged.

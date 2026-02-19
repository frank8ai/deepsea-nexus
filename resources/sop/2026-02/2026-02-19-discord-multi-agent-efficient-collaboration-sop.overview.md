# Overview

## Invocation
- Use for Discord tasks that are long-output, decomposable into 2-3 parallel tracks, or at risk of cross-topic drift.

## Skeleton
1. Classify request and risk.
2. Split and dispatch to researcher/coder/writer in parallel.
3. Persist full artifacts under `agent/`, `docs/`, `logs/`.
4. Main-agent converge and accept/reject.
5. Publish summary + paths only in main channel.

## Guardrails
- No direct worker-to-worker debate loops.
- New topic/project must move to new channel or isolated session.
- Auto-downgrade to draft if primary metric degrades for 2 monthly cycles.

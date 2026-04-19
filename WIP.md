# WIP

## Parked Research

### AutoSlay

- Explain what `AutoSlay` is in STS2.
- Document where the decompiled `AutoSlay` handlers live and what game flows they automate.
- Evaluate whether `AutoSlay` is useful for ProjectSpire or whether direct REST-driven game actions remain the cleaner control surface.
- Add the outcome to Lab documentation only after the research is complete.

### Console Hook, History, and Replay

- Add a direct server-to-dev-console execution path if the game exposes a stable command entry point.
- Persist recent console commands in mod-managed history.
- Expose REST endpoints for console execution and replay.
- Candidate endpoints: `POST /console/execute`, `GET /console/history`, `POST /console/replay-latest`, `POST /console/replay`.
- Decide whether replay should use history ids, offsets, or both.
- Document the execution model, safety constraints, and response payloads once implemented.

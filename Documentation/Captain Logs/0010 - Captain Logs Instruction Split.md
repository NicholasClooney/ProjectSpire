# 0010 - Captain Logs Instruction Split

This conversation records the reorganization of Captain Logs agent instructions out of the repository root guidance and into the Captain Logs folder.

Entries are newest first. This is not a transcript and it is not a replacement for full devlogs in `Documentation/Devlogs/`. Each entry preserves the interaction shape: user direction, agent response, user steering, outcome, and what future agents should carry forward.

## 2026-05-08 - Move Captain Logs Instructions Local

**Context:** The root `CLAUDE.md` Captain Logs section had grown too long and mixed folder-specific workflow rules into repository-wide guidance.

**User Direction:** The user asked to move the detailed Captain Logs instructions into `Documentation/Captain Logs/AGENTS.md`, add a `CLAUDE.md` symlink there, and keep the root `CLAUDE.md` reference clear that a Captain Log entry is still required after each meaningful conversation. The user also corrected the agent to avoid recording this unrelated documentation refactor in the Neow's Cafe theme log.

**Agent Response:** The agent extracted the detailed Captain Logs workflow into a folder-local `AGENTS.md`, created `Documentation/Captain Logs/CLAUDE.md` as a symlink to it, shortened the root `CLAUDE.md` section while preserving the Captain Log requirement, updated `README.md` repo structure notes, and created this separate conversation log.

**User Feedback:** The user wanted the Captain Logs instruction split documented separately rather than appended to the prior theme conversation.

**Outcome:** Captain Logs workflow rules now live next to the files they govern, root guidance stays concise, and the documentation refactor has its own Captain Log.

**Carry Forward:** When reorganizing instructions for a folder-specific workflow, keep the root pointer explicit about the required behavior and put the detailed procedure in the folder it governs.

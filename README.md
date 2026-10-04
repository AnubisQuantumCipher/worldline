# Claude lead isolation repository (WORLDLINE Phase One)

Purpose: a dedicated local repository whose linked git worktree(s) give the background session a guard-compatible
isolated edit destination inside the authorized handoff scope (the session background-isolation guard refuses Write/Edit
in the shared work tree, EnterWorktree cannot resolve HEAD because ~/.git is a stray info-only directory, and there is
no other git repository here). Local only: never pushed. Created 2026-10-04 by the Claude Code lead.

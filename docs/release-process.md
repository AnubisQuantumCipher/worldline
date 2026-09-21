# Release process and its boundaries (1.3.0)

This document states what each step of a release proves and, as importantly, what it does not.
The mechanism is in `.github/workflows/assurance.yml`, `.github/workflows/release.yml`,
`scripts/assurance.py`, `scripts/release_gate.py` and `scripts/release_notes.py`; the dry-run
rejection tests are `tests/test_release_gate.py`.

## The rule

A version may be published only when a full assurance run of the **exact commit** the tag names
passed, in the same workflow run, and the gate accepted that report for that commit and tree.
"Latest green CI on main", a run of another commit, a partially successful run, a skipped or
cancelled step, or a source-only manifest check presented as a fresh proof are all rejected by
name (`scripts/release_gate.py`).

## Steps

1. **Assurance** (`assurance.yml`, read-only token). Check out the full commit id, verify the
   checkout is that commit, then `scripts/assurance.py run --expect-sha <sha>`: build the kernel
   and test binaries, run the Ada behaviour tests and the fuzz, the Python suite (which includes
   the deterministic freshness regressions A–J and the gate tests), the SPARK proof gate re-run
   on this build, and the proof-manifest verification with the library checked. Each step's exit
   status, duration and log digest, the commit and tree, the runtime version and the toolchain
   identities are written to `assurance.json`; the result is `PASS` only if every required step
   succeeded, the tree was clean, and the regenerated proof manifest covers the committed source
   set with zero exceptions and at least the floor.
2. **Gate** (`release.yml`, publish job, write token, runs no tests). Resolve the tag to its
   commit and tree; build `worldline-<tag>.tar.gz` with `git archive` from that commit and check
   it unpacks to exactly the tracked files; compute digests; read the remote tag target and
   whether a release already exists; run the gate with all of it. A draft left by an earlier
   failed attempt of the same commit is removed; a published release is never touched.
3. **Draft, verify, publish, verify.** Create the release as a draft with the archive, its
   `.sha256`, `release-manifest.json` and `assurance.json`; download the draft's assets and
   compare them byte-for-byte with what was built; check the release target is the commit; then
   publish; then fetch the published release independently and verify the digests against the
   manifest. A mismatch at any point leaves the release unpublished (draft) and the job red.
4. **Notes** are generated from the `CHANGELOG.md` section plus the numbers in `assurance.json`
   (test counts, proof totals, library hash, toolchain). Nothing is typed from memory.

## Boundaries (what a green release does and does not say)

- **Historical evidence vs current eligibility.** A world's finalization evidence is history: it
  says what passed under the requirements of that moment. Eligibility to promote is decided now,
  against the current PRIME's requirement identity. The two coincide only when nothing that
  matters changed; otherwise `revalidate`.
- **Candidate bytes vs staged bytes.** The candidate is what the agent produced and the checks
  ran on. The staged result is a three-way merge of that onto the current PRIME. They are the
  same bytes only when PRIME did not move; when it did, the staged result needs its own passing
  validation or the kernel refuses it.
- **Requested vs reported model identity.** The adapter argv records what was requested
  (`-m …`); a provider/client-reported identity is recorded only where the adapter's event
  stream carries one (claude: `init.model`, `modelUsage`; codex JSONL carries only a thread id).
  Neither is proof of what model answered.
- **Python vs SPARK.** The kernel proves state-machine rules and equality verdicts over the
  identities it is handed (130 checks, nothing assumed). Everything that decides *what* is
  hashed and compared — manifests, contexts, requirement identities, the exchange, the sandbox —
  is Python and is covered by tests, not proof.
- **Local vs pushed vs merged vs tagged vs released.** A commit on a branch proves nothing about
  main. A pull request's assurance is of the PR head. The release gate accepts only an assurance
  of the tagged commit itself, produced in the same run; merging does not carry a branch's green
  over.
- **Published vs installed.** Publication makes an archive available with a verified digest. It
  does not install it anywhere; `install.sh` runs its own gate (build, tests, proof, backups)
  on the machine that installs.
- **Signing.** The archive digests are recorded in the release manifest and verified after
  publication; tags and assets are `unsigned` unless the manifest says otherwise. That is a
  recorded fact, not a claim of provenance beyond the GitHub account that pushed the tag.
- **Source-only archive.** The proved library is not shipped; the installer rebuilds it and
  re-runs the proof gate, and the library hash on another machine or architecture may differ
  from the one recorded by the assurance run.

## Operator recipe

```
# on the merged commit, after the workflow files are in main:
git tag -a v1.3.0 -m "WORLDLINE 1.3.0" <merged sha>
git push origin v1.3.0                 # triggers release.yml at that commit
gh run watch                            # resolve -> assurance -> publish
gh release download v1.3.0 --dir /tmp/v && (cd /tmp/v && sha256sum -c worldline-v1.3.0.tar.gz.sha256)
```

Never push a version tag while a workflow that could publish without assurance is still the one
the tag's commit carries: the release workflow that runs is the one at the tagged commit.

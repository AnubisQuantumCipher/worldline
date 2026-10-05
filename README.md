# WORLDLINE Phase One engineering checkpoint

**Work in progress. Phase One is not complete or accepted.**

This branch publishes the isolated engineering work through local source commit
`8c5ad29d2dff4db2d91631fe5d3d808fa3c5e4ac`. It preserves the design drafts, source packets,
frame implementation drafts, recorded reviews, outstanding findings and obligation ledger.

The integrated development branch is
[`codex/phase1-resource-kernel-20260930`](https://github.com/AnubisQuantumCipher/worldline/tree/codex/phase1-resource-kernel-20260930).
This checkpoint comes from a separate local repository and has independent history;
it is an engineering archive, not a merge-ready runtime branch.

## Where to start

- [Status and open work](STATUS.md)
- [Draft enforcement core](lanes/frame-v6-w1-enforcement-v1/SELFCHECK.md)
- [Draft setup package and gaps](lanes/frame-v6-w1-setup-v1/GAP.md)
- [Source packets](packets/)
- [Designs and their review records](designs/)
- [Original obligation ledger](workflow/ledger.json)

Frame adoption, required full strict proof, matching-source runtime evidence,
final acceptance, publication of the integrated candidate and deployment remain
subject to their original requirements. Historical source/design review verdicts
retain their recorded model provenance and scope; this upload grants no acceptance.
No build, proof campaign, privileged setup or runtime installation was performed
for this publication.

## Publication provenance

[PUBLICATION-MANIFEST.json](PUBLICATION-MANIFEST.json) records the source identity
and hashes of the included files. Their contents and executable modes are retained;
the original local README is preserved as
[historical/LOCAL-README.md](historical/LOCAL-README.md).

The separate publication history removes session-link trailers from commit messages
and omits the unrelated `backup-repair-packet/` notes, which contain private device
and vault identifiers. Original local commits, files and evidence remain untouched.
[PUBLICATION-HISTORY.json](PUBLICATION-HISTORY.json) maps the original commits to
the publication commits. Earlier documents describing the repository as local-only
are historical records predating this publication.

Checks for this upload cover source/file identity, scoped history transformation,
credential and session-link patterns, file sizes and remote commit readback. They
do not replace independent engineering review, formal proof or runtime validation.

"""The one definition of what a complete assurance run must contain.

Two rosters that can disagree is the same defect as two resolvers that can disagree. The release
gate refuses a report whose required-step list differs from its own, so a roster added in one
place and not the other is an integration failure rather than a silent gap — but the fix is to
have one list, not two that are checked against each other.
"""
from __future__ import annotations

#: Every step a complete assurance run must contain, in order. Adding one here makes it required
#: for both the run and the release decision at the same time.
REQUIRED_STEPS: tuple[str, ...] = (
    "checkout-identity",
    "clean-build-tree",
    "build",
    "ada-tests",
    "ada-fuzz",
    "python-tests",
    "evaluation-domain",
    "proof-gate",
    "proof-manifest",
)


# The preserved vulnerable build that the evaluation-domain gate runs as its control arm.
#
# It is pinned by BOTH the commit and the `runtime` subtree, because a tag is a movable
# pointer. If the tag were quietly re-pointed at a repaired build, the control would start
# passing, the gate would report the instrument healthy, and the candidate arm would be the
# only thing left — which is exactly the failure this control exists to prevent. The subtree
# is pinned as well so a commit rewrite that preserves the tag name cannot change the bytes
# that are actually executed.
#
# This commit is deliberately NOT released. It is kept for as long as the evaluation-domain
# property is claimed.
COUNTEREXAMPLE_TAG = "counterexample/verifier-bytes-without-evaluation-domain"
COUNTEREXAMPLE_COMMIT = "1bd5c0890e1c2686b3e33389831c76fe1f5cc25b"
COUNTEREXAMPLE_RUNTIME_TREE = "1c628de542bfc843f5f5e1aaa0580a0c4b12c40e"

#!/usr/bin/env python3
# Read-only stale-text sweep for v8. The v6-and-earlier expansion is unchanged from v7
# (already swept and accepted at v7 review); v8 touches only 9 v7 lines, supersedes V7-H,
# and adds new v8 sections. So we (1) confirm the 9 corrected strings are resolved,
# (2) confirm the superseded/old strings are absent from the reader-visible v8 text,
# (3) search the v8 own-authored text + corrected carried lines for stale classes.
import re
D = "/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs"
V7 = open(f"{D}/claude-root-worker-seam-design-v7/SEAM-DESIGN.md", encoding="utf-8").read().split("\n")[:-1]
V8 = open(f"{D}/claude-root-worker-seam-design-v8/SEAM-DESIGN.md", encoding="utf-8").read().split("\n")[:-1]

# R8 result texts
raw8 = "\n".join(V8)
r8 = {}
for m in re.finditer(r"\*\*R8-(\d+) replaces v7 line (\d+).*?\n```text\nv7:\n(.*?)\nv8:\n(.*?)\n```", raw8, re.S):
    r8[int(m.group(2))] = (m.group(1), m.group(3), m.group(4))

# reader-visible carried v7 prose: the three slices, with R8 applied, V7-H (1107-1124) dropped,
# and the §B.2 R7 result lines already live in C7-B (we take v7 lines as-is with R8 overrides).
carried_slices = [(128,865),(933,1104),(1127,1403)]
# drop fenced OLD-text (between ```text and the v7:/v8: marker, and between the result marker
# and the closing ```) so only reader-visible live text + result text remains.
def live_mask(L):
    mask = [True]*(len(L)+1)
    inf = False; mode = None
    for i in range(1,len(L)+1):
        l = L[i-1]
        if l.startswith("```"):
            mask[i] = False; inf = not inf; mode = "old" if inf else None; continue
        if inf and re.fullmatch(r"v[0-9]+:", l):
            j = i+1; later = False
            while j <= len(L) and not L[j-1].startswith("```"):
                if re.fullmatch(r"v[0-9]+:", L[j-1]): later = True
                j += 1
            mask[i] = False; mode = "old" if later else "new"; continue
        if inf and mode == "old":
            mask[i] = False
    return mask
mask = live_mask(V7)
carried = []
for a,b in carried_slices:
    for i in range(a,b+1):
        if not mask[i]: continue
        line = r8[i][2] if i in r8 else V7[i-1]
        carried.append((f"v7:{i}", line))

# v8 own-authored lines: everything outside carried-slice echoes — i.e. the v8 file's own sections.
# We take all v8 lines that are NOT inside the §B.2 fenced R8 old-text (to avoid matching the quoted v7 text).
own = []
inf = False
for i,l in enumerate(V8,1):
    if l.startswith("```"): inf = not inf; continue
    if inf: continue
    own.append((f"v8:{i}", l))

text = carried + own + [(f"R8-{r8[k][0]}", r8[k][2]) for k in r8]

# (1) targets resolved — these must be ABSENT from reader-visible carried prose
gone = {
  "handler-unchanged": r"the original exception handling is unchanged|the `elif` becoming the plain alternative|becomes the plain alternative",
  "daemon-390-393-as-send": r"request's writer \(`:390-393`\)|by detached work \(`:390-393`\)",
  "launch-703-708": r"\(`:703-708`\)",
  "launch-729-731": r"`:729-731`|runtime\.py:729-731",
  "launch-732-736": r"`:732-736`",
  "launch-732-735": r"runtime\.py:732-735",
  "front-owners-loose": r"The front's owners are closed",
  "v1s-parameters": r"roster is V1's",
}
for name, pat in gone.items():
    hits = [t for t in carried if re.search(pat, t[1])]
    print("RESOLVED" if not hits else "STILL-PRESENT", name, [h[0] for h in hits])

# (2) the superseded V7-H lines must not appear as reader-visible (they are dropped, not in a slice)
vh = [V7[i-1] for i in range(1107,1125)]
# confirm none of the three slices covers 1107-1124
assert all(not (a<=k<=b) for a,b in carried_slices for k in range(1107,1125))
print("V7-H dropped: slices do not cover 1107-1124: ok")

# (3) stale-class scan over the full reader-visible v8 text
P = {
  "capacity_stride": r"WL_ABI_CAPACITY|\bstride\b",
  "d4a_dependence": r"(needs|depends on|until|unless)[^.]{0,60}D-4a|selected specification",
  "pidfd_only": r"pidfds? (are |is )?terminal|both pidfds",
  "rc_installed_old": r"\bRC-1[0-2]\b",
  "oom_kill_claim": r"result = oom-kill|returns `oom-kill`",
  "as_in_original": r"as in the original",
  "unchanged_claim": r"handling is unchanged|phase follows the committed custody phase, so after",
}
for name, pat in P.items():
    hits = [t for t in text if re.search(pat, t[1])]
    print(f"CLASS {name}: {len(hits)}")
    for h in hits[:12]:
        print("   ", h[0], "|", h[1][:140])

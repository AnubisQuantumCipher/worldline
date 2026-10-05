#!/usr/bin/env python3
# Read-only verification for seam design v8. Reads files, prints to stdout, writes nothing.
import re, hashlib, json, sys
D = "/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs"
def lines(p):
    t = open(p, encoding="utf-8").read().split("\n")
    assert t[-1] == "", p
    return t[:-1]
F = {k: lines(f"{D}/claude-root-worker-seam-design-{k}/SEAM-DESIGN.md") for k in ("v1","v2","v3","v4","v5","v6","v7")}
V8 = open(f"{D}/claude-root-worker-seam-design-v8/SEAM-DESIGN.md", encoding="utf-8").read().split("\n")
RJ6 = json.load(open(f"{D}/claude-root-worker-seam-design-v6/review/claude-v1/review.json"))
RJ7 = json.load(open(f"{D}/claude-root-worker-seam-design-v7/review/claude-v1/review.json"))
probs = []

# v7 base identity
b7 = open(f"{D}/claude-root-worker-seam-design-v7/SEAM-DESIGN.md","rb").read()
print("v7", hashlib.sha256(b7).hexdigest(), len(F["v7"]), "lines")

# slices
S = [(m.group(1), int(m.group(2)), int(m.group(3)), m.group(4))
     for m in re.finditer(r"^\| (C7-[A-Z]+) \| (\d+)-(\d+) \| `([0-9a-f]{64})` \|", "\n".join(V8), re.M)]
cov = set()
for n,a,b,h in S:
    hh = hashlib.sha256("".join(x+"\n" for x in F["v7"][a-1:b]).encode()).hexdigest()
    if hh != h: probs.append(("slicehash", n))
    r = set(range(a,b+1))
    if cov & r: probs.append(("overlap", n))
    cov |= r
print("slices", len(S), "ok" if not any(p[0] in ("slicehash","overlap") for p in probs) else "BAD")
sup = [(1,127),(869,930),(1107,1124),(1406,1526)]
for a,b in sup:
    r = set(range(a,b+1))
    if cov & r: probs.append(("supoverlap", a))
    cov |= r
uncov = [i for i in range(1,len(F["v7"])+1) if i not in cov and F["v7"][i-1] not in ("","---")]
if uncov: probs.append(("uncovered", uncov))

# R8 blocks
blocks = []
i = 0
while i < len(V8):
    m = re.match(r"^\*\*R8-(\d+) replaces v7 line (\d+) \(in (C7-[A-Z]+)", V8[i])
    if m:
        num = int(m.group(1)); a = int(m.group(2)); sl = m.group(3)
        assert V8[i+1] == "```text", num
        assert V8[i+2] == "v7:", (num, V8[i+2])
        j = i+3; old = []
        while V8[j] != "v8:": old.append(V8[j]); j += 1
        j += 1; new = []
        while V8[j] != "```": new.append(V8[j]); j += 1
        if old != F["v7"][a-1:a-1+len(old)]: probs.append(("oldquote", num))
        if len(old) != 1: probs.append(("multiline", num))
        if old == new: probs.append(("nochange", num))
        blocks.append((num, a, sl, old, new)); i = j
    i += 1
nums = [b[0] for b in blocks]
print("R8 blocks", len(blocks), "contiguous", nums == list(range(1,len(nums)+1)))

# slice membership + no prior R + not twice + not superseded
def rows(ver, prefix):
    return [(mm.group(1), int(mm.group(2)), int(mm.group(3)))
            for mm in re.finditer(r"^\| ("+prefix+r"[A-Za-z0-9-]+) \| (\d+)-(\d+) \|", "\n".join(F[ver]), re.M)]
slmap = {}
for n,a,b,h in S:
    for k in range(a,b+1): slmap[k] = n
# prior R targets in v7 (R8 must not hit a v7 line that is itself machinery we must not double-edit;
# but R8 targets v7 lines; "earlier R" protection = none of these v7 lines is targeted by another R8)
seen = {}
for num,a,sl,old,new in blocks:
    if slmap.get(a) != sl: probs.append(("slicename", num, slmap.get(a), sl))
    if a in seen: probs.append(("double", num, a))
    seen[a] = num
    if any(a in range(x,y+1) for x,y in sup): probs.append(("insuperseded", num))

# required-change texts verbatim
raw = "\n".join(V8)
for rc in RJ7["required_changes"]:
    ch = rc["change"]
    # the design escapes inner double-quotes as \" in the §A.1 cell
    cand = ch.replace('"', '\\"')
    if ch not in raw and cand not in raw: probs.append(("reqquote", rc["id"]))
# rulings verbatim from v6 review.json
for r in RJ6["rulings"]:
    for fld in ("ruling","owner","evidence_required"):
        if f'"{r[fld]}"' not in raw: probs.append(("ruling", r["id"], fld))

# handler before/after: after == before minus :192, elif->else, plus phase line; quarantine in else
def block_after(marker):
    k = raw.index(marker)
    seg = raw[k:]
    blks = re.findall(r"```python\n(.*?)\n```", seg, re.S)
    return blks
pyblk = re.findall(r"```python\n(.*?)\n```", raw, re.S)
if len(pyblk) != 2: probs.append(("pyblocks", len(pyblk)))
else:
    before, after = pyblk
    if "self.phase='UNKNOWN_WORKER_OWNERSHIP'" in after.split("\n")[0:2] and "except" in after: pass
    # checks:
    if "self.phase='UNKNOWN_WORKER_OWNERSHIP'" in after: probs.append(("after_has_192",))
    if "elif self.phase==" in after: probs.append(("after_has_elif",))
    if "else:" not in after: probs.append(("after_no_else",))
    # quarantine must be under the else, not the if
    ca = after.split("\n")
    qi = [n for n,l in enumerate(ca) if "p.quarantine(operation,error)" in l]
    ei = [n for n,l in enumerate(ca) if l.strip()=="else:"]
    if not qi or not ei or qi[0] < ei[0]: probs.append(("quarantine_not_in_else",))
    if "self.phase=self.committed_front_phase(operation)" not in after: probs.append(("no_phase_set",))
    # before must have the elif and :192
    if "self.phase='UNKNOWN_WORKER_OWNERSHIP'" not in before or "elif self.phase==" not in before:
        probs.append(("before_wrong",))

# tables cell counts
inf = False; hdr = None
for k,l in enumerate(V8,1):
    if l.startswith("```"): inf = not inf; continue
    if inf: continue
    if l.startswith("|"):
        c = len(re.findall(r"(?<!\\)\|", l))
        if k>1 and V8[k-2].startswith("|") and not re.match(r"^\|[\s:-]+\|", l):
            if hdr is not None and c != hdr: probs.append(("cells", k, c, hdr))
        if not (k>1 and V8[k-2].startswith("|")):
            hdr = c
    else:
        hdr = None

# dangling R8 refs
refs = {int(x) for x in re.findall(r"R8-(\d+)", raw)}
if refs - set(nums): probs.append(("danglingR8", sorted(refs-set(nums))))

for ph in ("TODO","TBD","XXX","<!--"):
    if ph in raw: print("marker:", ph, raw.count(ph))

print("PROBLEMS", probs if probs else "none")

# PK-0 v2 drafting author: process record (preserved; disclosed)

**Who.** The C-API drafting agent (`a15cbfbc1dbf895f6`). The lead resumed it ~15:54Z on 2026-10-05, in a new Claude Code
session, to answer PK0-RC1..RC5 of the sealed PK-0 v1 review (`packets/capi-pk0/review/gpt61-v1`, review.json
`fc615b5be33f0caf4e2964e06b2d001d2568c12088c9ca306bb8500bd70dbdf5`). It handed back ~16:45Z as a reply (the handback
tool was unavailable). That report is model output, recorded as stated.

## What the lead verified (engineering only, not review)

- **Packet files.** All nine `packets/capi-pk0-v2` files equal the hashes in the report and in `packet.json`
  (`c5ce00cd…`).
- **v1 unchanged.** The v1 packet is untouched: packet.json is still `9808145e…`, and all six v1 payload hashes appear in
  v2's change list.
- **Bound inputs.** All 100 entries in `bound_inputs_relative_to_L0` match L0 (`work/claude-composition-v5-beta/source`)
  by sha256 and size.
- **Payload paths.** None of the six payload paths exists in L0.
- **Parse checks.** Every JSON file loads, and every Python file parses as an AST. Nothing was imported or run.

## Disclosures

1. **Lead transcription error.** The lead's resume message gave the v1 review.json as `fc615b5b0d75…`. The frozen and
   observed value is `fc615b5be33f…`. The author found the mismatch and used the frozen value (its deviation 1).
2. **Fixture difference.** The new U15y collapse requests add Resulting_Requirement, which the S5 fixtures' requests do
   not have. The author reports that S5's own unexecuted tests assert AUTHORIZED for a request without one, contrary to
   `core/worldline-collapse.ads`. This is related to author finding F32 in STATUS. S5 was not edited.
3. **Coverage stated as not exercised.** Two groups are listed as not exercised rather than covered.
4. **Header test.** It now fails rather than skips when `WORLDLINE_PK0_SCRATCH` is unset.
5. **Launch requirements.** Six launch obligations stay OPEN; source cannot establish them.
6. **Nothing run or interrupted.** The author reports no execution, no interruption, writes only under
   `packets/capi-pk0-v2/`, one `sia.ask`, no notes, and all eight Ada skills loaded. JACKAL J28–J33 were exact; J31 is
   recorded as unused.

## What this does not change

Nothing here grants anything. PK0-RC1..RC5 stay open until PK-0 v2's own independent actual gpt-6.1-sol review rules.
The PK-0 stage gate, the baseline run in an admitted frame, remains OPEN.

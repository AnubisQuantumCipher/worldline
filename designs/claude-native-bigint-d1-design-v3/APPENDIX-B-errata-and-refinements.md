# Appendix B to D1 DESIGN v3: errata and one structural refinement

Status: **DRAFT for independent actual gpt-6.1-sol review.**

- This appendix was written after `DESIGN.md` in the same create-only package. The files are create-only, so
  `DESIGN.md` itself is not edited.
- Where an item below differs from `DESIGN.md`, this appendix governs.
- Nothing here was compiled, proved, run or accepted. Every obligation stays OPEN.

## B.1 Errata (text defects found on read-back)

| Id | DESIGN.md location | Defect | Corrected text |
|---|---|---|---|
| E-1 | §2, input-identity table, row for `HANDOFF.md` / `START-CLAUDE.txt` / `complete-phase1-prompt.txt` | the cell is garbled ("`004c71a8…bf588237`-prefix differs: …"). The note directly below the table already gives the right values | `HANDOFF.md` `2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237`; `START-CLAUDE.txt` `004c71a8da3cb4e917812af427a1701bde226a18da615bcdbf483414d75f187e`; `complete-phase1-prompt.txt` `1b228f4b07209c91c8f8770851906a8ebbf90db12f0af605954aff392946b327` [OBS `sha256sum`] |
| E-2 | §9.2, first table row | the citation `runtime/worldline/resource_run_ledger.py:246` is off by two | `runtime/worldline/resource_run_ledger.py:248` (`if status!=0:raise CoreUnavailable('full-ledger native transport refused')`) [OBS] |
| E-3 | §5.6, `Lemma_Order_Extension` (LA-4) Pre | `Low_L in 0 .. P - 1` is a range membership on the private type `Big_Integer`, which is not legal Ada | `Pre => P > 0 and then Low_L >= 0 and then Low_L < P and then Low_R >= 0 and then Low_R < P and then D_L <= 255 and then D_R <= 255` |
| E-4 | §7.5, CL-2 code | `Start_Of (N, Negative)` names an undefined helper | `(if Negative then N.First + 1 else N.First)`, exactly as in §6.6 |
| E-5 | §2, "Chapters read" | when the sentence was written, three chapters had not yet been opened in this session | they were then read in full: `SK/spark-users-guide/chapters/ch13-pointers-and-ownership.md`, `SK/advanced-ada/chapters/ch13-exceptions.md` and `SK/advanced-ada/chapters/ch16-access-types.md`. The statement is now true. B.2 applies one consequence of ch13 |

## B.2 Structural refinement of CL-1: move the handler to an inner block (supersedes the shape of DESIGN.md §6.6 and §7.2)

**Reason [LEAD; DOC `SK/advanced-ada/chapters/ch13-exceptions.md`, RM 11.6 optimization permissions].**

- When an exception results from the failure of a language-defined check, Ada permits assignments made in the
  sequence of statements protected by the handler to be disrupted. Such an object may be abnormal when the handler is
  reached.
- An example of such a check is `Storage_Check`, for allocation or stack exhaustion. That is exits X2, X4 and
  possibly X5 in DESIGN.md §7.1.
- In DESIGN.md §6.6 the owner assignment `Work := new …` lies inside the handled sequence of the function-level
  handler. A handler that reads `Work` would therefore rely on behaviour the language does not guarantee.
- Moving the handler to an inner block that encloses only the `Decide_Work` call puts the assignment **before and
  outside** the handled sequence. The refinement relies on no store ordering inside that sequence.

**Refined body.** Everything else is as DESIGN.md §6.6. UNCOMPILED / UNPROVED.

```ada
   function Integer_Matches
     (A : Bytes; J : Span; N : Node; T : Span; Sign, Magnitude : Node) return Boolean
   with Global => null
   is
      B        : constant Binary_String := Base64 (A, T, Magnitude);
      Negative : constant Boolean := Byte_At (A, J, N.First) = Character'Pos ('-');
      Work     : Work_Access;
      Result   : Boolean;
   begin
      if not N.Valid or else N /= Prefix (A, J, 0) or else N.Form /= Integer_Value
        or else N.After /= J.Length or else not B.Valid
        or else not Sign.Valid or else Sign.Form /= Boolean_Value
        or else (Negative /= Match (A, T, Sign.First, "true"))
        or else (B.Length > 0 and then Binary_At (A, T, B, B.Length - 1) = 0)
        or else (Negative and then B.Length = 0)
      then return False; end if;                     --  verbatim guard; nothing allocated
      Work := new P.Bytes'[1 .. B.Length => 0];      --  X2 (allocation failure) propagates directly: nothing owned yet
      begin                                          --  the handled sequence contains only the call
         Decide_Work (A, J, (if Negative then N.First + 1 else N.First), N.After, T, B, Work.all, Result);
      exception
         when others =>
            Free_Work (Work);                        --  Work was assigned before this sequence began
            raise;                                   --  the same occurrence; never converted to a value
      end;
      Free_Work (Work);
      return Result;
   end Integer_Matches;
```

Consequences:

- The inner block has no loop, so F19's unsupported construct does not arise. All loops remain in `Decide_Work`,
  `Multiply_Add` and the ghost procedures.
- Exits X1, X3, X4, X6 and X7 behave as in DESIGN.md §7.1. Exit X2 now propagates from outside the inner block, with
  `Work` still null and nothing to reclaim.
- The probe battery P-W1..P-W8 applies to this shape:
  - P-W1 checks a handler on a block statement inside a non-allocating `Global => null` function, with a bare
    `raise;`.
  - P-W3's unreachable-code risk (DESIGN.md F21, F22) is unchanged. If P-W3 fails, the lead-owned CL-2 (frame
    lifetime) or CL-3 (`finally`) applies, as in DESIGN.md §7.5.
- P-W6, native evidence, additionally inspects the generated code for the owner store and the handler's landing pad.
- CL-2 has no handler and is unaffected. CL-3's `finally` part would sit on the same inner block, for the same reason.

## B.3 Unchanged

- Everything not listed here stands as written in `DESIGN.md`.
- All obligations, operator packages, controls and OPEN items stand as written.
- No option is selected for the operator.

_End of Appendix B._

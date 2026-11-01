**This is a concrete dependency/compiler compatibility failure, materially distinct from the exhausted D158 receipt/progress review. It does not reset that history or authorize another execution.**

The failed native build identifies:

```text
gnatcoll-boyer_moore.adb:77:06:
warning: renamed predefined unit is an obsolescent feature (RM J.1) [-gnatwj]
```

At `W/source/gnatcoll/minimal/src/gnatcoll-boyer_moore.adb:77`, the body imports `Unchecked_Deallocation`; lines 248–250 instantiate it twice. The pinned original has identical bytes:

- Upstream: `AdaCore/gnatcoll-core@1d4374ae9187fd14d42ca99a3deb0ab2ff1ebc55`
- Git blob: `6fa9d24d0a3e0ae7b264f36bc4a32acd9f579df6`
- Original/staged SHA256: `8559ffbde746e34833294f631548b4536606ca29bacd849213ab9842d4018ece`
- Acquisition provenance: `old-retirement-xgen-source-cut-v1/source-receipts.jsonl:249`.

The strict failure is expected: original `minimal/gnatcoll_minimal.gpr:113–115` enables `-gnatwaCJe`, including warnings-as-errors. Actual partial `W/gnatcoll/obj/gnatcoll_minimal/static/gnatcoll-promises.ali:1–19` records `-gnatwa`, `-gnatwe`, checks, DEBUG/O0 and the additional strict flags. No warning weakening is needed.

The smallest prospective adaptation is an explicitly derived body with these changes only:

```diff
-with Unchecked_Deallocation;
+with Ada.Unchecked_Deallocation;
@@
-      procedure Internal is new Unchecked_Deallocation
+      procedure Internal is new Ada.Unchecked_Deallocation
         (Offset_Array, Offset_Array_Access);
-      procedure Internal is new Unchecked_Deallocation (String, String_Access);
+      procedure Internal is new Ada.Unchecked_Deallocation
+        (String, String_Access);
```

The final line wrap preserves the existing style discipline. Changing only the context clause would leave the two unqualified generic names unresolved.

Local runtime evidence supports canonicalization:

- `G/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude/unchdeal.ads:16–23` explicitly identifies the legacy unit as the renaming of `Ada.Unchecked_Deallocation`, with generic formals `Object` and `Name`, and intrinsic import.
- `…/a-uncdea.ads:19–31` defines the canonical unit with matching formals and intrinsic import; it additionally states nulling and dependency contracts.
- SHA256 respectively:
  - `fd64801906c9528e0bf3a49c076ec90e14301ea512f6b42d05f989107b817aa4`
  - `a4d60bcca23afe38f574c5340b02d7744361cc07a5e8e37213d57b8f3fd6fbc2`

This supports unchanged intended deallocation semantics; **the adapted build and behavioral equivalence remain untested/unproved**. Retain the exact selected original, record its preimage hash, prospective patch, derived-body hash and distinct provenance. Never relabel the derivative as the selected upstream commit.

Alternatives are less suitable:

- Local generic renaming adds another declaration and visibility obligation.
- Changing compiler, upstream commit, or omitting this unit broadens compatibility and qualification scope.
- Suppressing the warning or weakening strict flags violates the task constraints.

Future verification should cover:

1. Exact three-site adaptation and unchanged surrounding algorithm/API.
2. Clean strict minimal build, then core/helpers and full generator qualification; additional diagnostics remain possible.
3. Bounded Boyer–Moore lifecycle checks: successful/unsuccessful and case-sensitive/insensitive search; `Compile → Search → Free`; repeated `Free` and reuse after `Free`, with checks enabled.
4. Both `Free` instantiations still operate on the same access types and null their respective fields; allocation/pool/finalization behavior stays unchanged.
5. Fresh complete dependency hashes and downstream translator evidence. Partial failed objects cannot qualify readonly reuse.

`core/src/gnatcoll-email-mailboxes.adb:29,39` directly consumes Boyer–Moore; dependency validation must therefore extend beyond compiling the modified unit.

**Configuration update:** actual `target.stdout` and `version.stdout` now read `aarch64-linux-gnu` and `16.1.0`, confirming the earlier expected compiler identity strings for this attempt. No `.cgpr` exists in the inspected failed `W`, including hidden/ignored paths. Actual selected CGPR bytes and runtime/tool-resolution provenance therefore remain open; the partial ALI is useful compiler-switch evidence, not a replacement.

Failure evidence hashes:

```text
minimal.stdout  98cc3e89db4d9f8870dc965df0bbf3682f0dbd73e55e88aab225de90b7c906eb
minimal.stderr  0e7b89340aa18d5f0879c73acd27d02a0ac6c2417d4a1601b5d5e70cfa1c8e7b
target.stdout   811b17aa02eb472140fbd7c338e99ac8770181c999ed2ea78797163dfd0fbd5b
version.stdout  32432b1207472725d2ff242a3c804108d734db278bc9013841d4c4992d090a6c
```

The smallest sound next step is a separate dependency compatibility dossier and reviewed derivative package. No implementation or rerun occurred here; failed `W` and sealed D158/D159 packages remain unchanged. Generation/recovery **UNRUN**. **F7 NOT PERFORMED.**
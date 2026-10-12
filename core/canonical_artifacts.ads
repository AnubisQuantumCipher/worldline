with Evaluation_Pending;
with Worldline;

-- Target canonical.py JSON grammar: UTF-8 scalar strings, shortest control
-- escapes, arbitrary decimal integers, null/bool, arrays, strictly sorted
-- unique decoded keys. No depth, number-of-rows or integer-value cap.
-- Storage, recursion, every parser/hash body and Python correspondence remain
-- mandatory proof obligations. A valid byte grammar does not prove custody.
package Canonical_Artifacts with SPARK_Mode is
   package P renames Evaluation_Pending;
   subtype Count is P.Count;
   subtype Bytes is P.Bytes;
   subtype Span is P.Span;
   use type Count;
   use type P.Byte;
   use type Worldline.Hash;
   type Span_Array is array (P.Index range <>) of Span;
   type Kind is (Invalid_Value, Null_Value, Boolean_Value, Integer_Value,
                 String_Value, Array_Value, Object_Value);
   type Node is record
      Valid : Boolean := False;
      Form : Kind := Invalid_Value;
      First, After : Count := 0;
   end record;
   No_Node : constant Node := (False, Invalid_Value, 0, 0);
   --  Full canonical JSON traversal is distinct from evaluation's nonfloat
   --  Node/Kind API. Float and integer remain different public JSON kinds.
   type JSON_Kind is
     (Invalid_JSON_Value, Null_JSON_Value, Boolean_JSON_Value,
      Integer_JSON_Value, Float_JSON_Value, String_JSON_Value,
      Array_JSON_Value, Object_JSON_Value);
   type JSON_Node is record
      Valid : Boolean := False;
      Form : JSON_Kind := Invalid_JSON_Value;
      First, After : Count := 0;
   end record;
   No_JSON_Node : constant JSON_Node := (False, Invalid_JSON_Value, 0, 0);
   function JSON_Prefix (A : Bytes; S : Span; From : Count) return JSON_Node
     with Global => null,
       Post => (if JSON_Prefix'Result.Valid then
         P.Valid (A, S) and then JSON_Prefix'Result.First = From
         and then From < JSON_Prefix'Result.After
         and then JSON_Prefix'Result.After <= S.Length
         and then JSON_Prefix'Result.Form /= Invalid_JSON_Value);
   --  Full exact canonical JSON bytes or those bytes plus exactly one LF.
   --  Native grammar/representation relation only, not source acquisition.
   function Canonical_JSON_Valid (A : Bytes; S : Span) return Boolean
     with Global => null,
       Post => (if Canonical_JSON_Valid'Result then P.Valid (A, S));
   -- Relative offsets avoid requiring First + Length to fit the index type.
   function Part (Whole : Span; First, After : Count) return Span
     with Global => null,
       Post => (if First <= After and then After <= Whole.Length
                then Part'Result.Length = After - First
                else Part'Result.Length = 0);
   function Prefix (A : Bytes; S : Span; From : Count) return Node
     with Global => null,
       Post => (if Prefix'Result.Valid then
         P.Valid (A, S) and then Prefix'Result.First = From
         and then From < Prefix'Result.After
         and then Prefix'Result.After <= S.Length
         and then Prefix'Result.Form /= Invalid_Value),
       Subprogram_Variant => (Decreases => S.Length - Count'Min (From, S.Length));
   function Canonical (A : Bytes; S : Span) return Boolean
     with Global => null;
   type Member is record
      Found : Boolean := False;
      Value : Node := No_Node;
      First, After : Count := 0;
   end record;
   No_Member : constant Member := (False, No_Node, 0, 0);
   function Field (A : Bytes; S : Span; Name : String) return Member
     with Global => null,
       Post => (if Field'Result.Found then
         Field'Result.Value.Valid
         and then Field'Result.First < Field'Result.After
         and then Field'Result.After <= S.Length);
   function String_Is (A : Bytes; S : Span; N : Node; Text : String)
      return Boolean with Global => null;
   function Root_Matches (A : Bytes; S : Span; Digest : Worldline.Hash)
      return Boolean with Global => null;
   -- Semantic correspondence to evaluation_terminal.value_bytes, including
   -- full arbitrary little-endian integer magnitudes and object insertion
   -- order independent of sorted canonical JSON keys. No caller truth flag.
   function Tagged_Matches (A : Bytes; JSON_Value, Tagged_Value : Span)
      return Boolean with Global => null,
        Subprogram_Variant => (Decreases => JSON_Value.Length);
   function Array_Payloads_Match
     (A : Bytes; JSON_Array : Span; Payloads : Span_Array) return Boolean
     with Global => null;
   -- A streaming view; omission is only the parsed top-level evidence root
   -- member plus the syntactically adjacent separator, never a text replace.
   type Hash_Result is record
      Valid : Boolean := False;
      Digest : Worldline.Hash := Worldline.Zero_Hash;
   end record;
   function Artifact_Hash (A : Bytes; S : Span; Evidence : Boolean)
      return Hash_Result with Global => null,
        Post => (if not Artifact_Hash'Result.Valid then
          Artifact_Hash'Result.Digest = Worldline.Zero_Hash);
   function Bindings
     (A : Bytes; Evidence, Environment, Context : Span;
      Payloads : Span_Array;
      Evidence_Root, Environment_Root : Worldline.Hash) return Boolean
     with Global => null;
   --  The exact canonical JSON projection of an ORIGINAL operation archive,
   --  without stripping a scoped S.record wrapper. canonical(S.record(...))
   --  sorts object names while the archive retains insertion order: match
   --  unique decoded names/cardinality, not an arbitrary object permutation
   --  of archive bytes. Arrays remain ordered; scalar tags/float bits exact.
   --  This relation requires canonical bytes (no optional file LF) and does
   --  not establish acquisition/file/row/source custody or authorize effects.
   --  Distinct borrowed arrays avoid concatenation and doubled extent limits.
   function Operation_Archive_JSON_Matches
     (JSON_Data, Archive_Data : Bytes; JSON_Value, Encoded : Span) return Boolean
     with Global => null,
       Post => (if Operation_Archive_JSON_Matches'Result then
         P.Valid (JSON_Data, JSON_Value) and then P.Valid (Archive_Data, Encoded));
   type Genesis_Correspondence is
     (JSON_Grammar_Unimplemented_Or_Invalid, Scoped_Archive_Invalid,
      Typed_Tree_Differs, Typed_Tree_Matches_Source_Custody_Open);
   -- exact_json permits canonical bytes or those bytes plus one trailing LF.
   -- Canonical source joins add finite binary64, Python's exact shortest repr,
   -- signed-zero bit identity and distinct float/integer tags at every depth.
   -- Evaluation Prefix/Canonical continue to reject fraction/exponent syntax.
   -- Matching this relation is not proof of file/row custody or authorization.
   --  Preserve the original Genesis dictionary order correspondence.
   function Genesis_Archive_Matches
     (A : Bytes; Genesis_File, Genesis_Row : Span) return Genesis_Correspondence
     with Global => null,
       Post => (if Genesis_Archive_Matches'Result = Typed_Tree_Matches_Source_Custody_Open
                then P.Valid (A, Genesis_File) and then P.Valid (A, Genesis_Row));
   --  Full typed-scope/canonical-file relation on separately leased original
   --  allocations, with no concatenation or combined extent bound.
   --  Canonical JSON sorts names; native S.record retains insertion order.
   --  Compare dictionary members by unique decoded names/exact cardinality,
   --  never by archive ordinal or rewriting either original archive. Arrays
   --  remain ordered; scalar types/float bits/Unicode stay exact. The same
   --  parser/typed matcher preserves legacy order in Genesis_Archive_Matches.
   --  Optional one LF; no byte acquisition or effect authority is established.
   function Scoped_Archive_JSON_Matches
     (JSON_Data, Archive_Data : Bytes; JSON_Value, Encoded : Span)
      return Genesis_Correspondence
     with Global => null,
       Post => (if Scoped_Archive_JSON_Matches'Result = Typed_Tree_Matches_Source_Custody_Open
         then P.Valid (JSON_Data, JSON_Value) and then P.Valid (Archive_Data, Encoded));
   --  Locate original canonical JSON field VALUE bytes, not a re-encoding.
   --  Same finite-float parser and optional one file LF; no original evaluation
   --  Prefix/Field grammar change. Empty span means absent/invalid input.
   --  Name uses inherited Field/String_Is spelling semantics. This locates
   --  bytes only: no source/scope/MAC/effect authority follows from a span.
   function Canonical_JSON_Field (A : Bytes; S : Span; Name : String) return Span
     with Global => null,
       Post => (if Canonical_JSON_Field'Result.Length > 0 then
         P.Valid (A, S) and then P.Valid (A, Canonical_JSON_Field'Result)
         and then Canonical_JSON_Field'Result.Length <= S.Length);
end Canonical_Artifacts;

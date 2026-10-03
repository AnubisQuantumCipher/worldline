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
end Canonical_Artifacts;
